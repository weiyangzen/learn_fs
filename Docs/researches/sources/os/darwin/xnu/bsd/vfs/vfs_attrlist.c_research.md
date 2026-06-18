# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_attrlist.c

## Scope And Role

`vfs_attrlist.c` implements Darwin/XNU VFS support for the `getattrlist`, `getattrlistat`, `fgetattrlist`, `getattrlistbulk`, `setattrlist`, `setattrlistat`, and `fsetattrlist` system call families. It translates user `struct attrlist` bitmaps into `vnode_attr` / `vfs_attr` requests, authorizes them, calls filesystem/VNOP backends where needed, synthesizes compatibility defaults, and packs or unpacks the fixed/variable-width attrlist ABI buffers.

This file is a VFS compatibility and ABI boundary layer: it hides filesystem differences while preserving legacy attrlist layout rules, 32-bit vs 64-bit time packing, Finder Info/resource fork conventions, volume attributes, APFS/firmlink-era extended common attributes, and directory bulk enumeration behavior.

## Main Data Structures

- `struct _attrlist_buf`: mutable packing state with base buffer, fixed cursor, variable cursor, allocated/needed sizes, actual returned attributes, and valid attribute masks.
- `struct getvolattrlist_attrtab`: table mapping volume/common attr bits to `vfs_attr` bits and packed field sizes.
- `struct getattrlist_attrtab`: table mapping object attr bits to `vnode_attr` bits, packed sizes, and required `kauth_action_t` authorization.
- `struct _attrlist_paths`: temporary storage for built full path, volume-relative path, and no-firmlink real path strings.

The core design is table driven: attr bitmaps are parsed into active vnode/vfs fields and expected fixed-buffer sizes before backend calls and packing.

## Attribute Packing

The file defines low-level packers for attrlist ABI layout:

- `attrlist_pack_fixed()` writes fixed-width fields and always advances by 4-byte-rounded size.
- `attrlist_pack_variable2()` writes an `attrreference` plus one or two variable data segments, used for ACL/filesec data.
- `attrlist_pack_variable()` is the single-variable wrapper.
- `attrlist_pack_string()` packs string `attrreference` metadata and null-terminated, 4-byte-aligned variable string data.
- `ATTR_PACK4`, `ATTR_PACK8`, `ATTR_PACK`, `ATTR_PACK_CAST`, and `ATTR_PACK_TIME` provide compact fixed-field helpers.

The implementation supports truncated caller buffers by advancing cursors according to required size while copying only what fits. With `FSOPT_REPORT_FULLSIZE`, the first `uint32_t` reports the full required entry size.

## Volume Attribute Path

`getvolattrlist()` handles requests with `volattr` set. It validates mount state, substitutes the mount root vnode when needed, parses requested volume/common attributes with `getvolattrlist_setupvfsattr()`, calls `vfs_getattr()`, optionally invokes MAC policy checks, synthesizes defaults for missing fields, and packs volume metadata.

Important synthesized/default behavior includes:

- default filesystem subtype `0`;
- default signature `0x4244`;
- default block size from `mnt_devblocksize`;
- derived used blocks from total/free blocks;
- default `VOL_CAP_INT_ATTRLIST`;
- default VFS-supported attribute/capability masks;
- root vnode ownership/mode/flags/encoding for common volume attributes.

Volume string attributes include volume name, mount point, mounted device, and filesystem type name. Filesystem type name packing verifies that the mount’s type-name reference did not change during packing and returns `ERESTART` if it did.

## Object Attribute Path

`getattrlist_internal()` is the central object getattr implementation. It:

1. Validates buffer size and attrlist bitmap count.
2. Handles a fast statfs-like volume subset.
3. Enforces that volume attrs are not mixed with file/dir attrs except allowed extended-common behavior.
4. Validates `FSOPT_ATTR_CMN_EXTENDED`, `FSOPT_PACK_INVAL_ATTRS`, and legacy bit reuse rules.
5. Builds a `vnode_attr` request using `getattrlist_setupvattr()`.
6. Authorizes required vnode actions.
7. Calls `vnode_getattr()` when active vnode attributes are required.
8. Applies MAC filtering with `mac_vnode_check_getattr()`.
9. Packs results through `vfs_attr_pack_internal()`.

`vfs_attr_pack_internal()` is the reusable packer used by normal getattr and by bulk/native pack paths. It computes variable sizes, builds requested paths, handles unsupported backend attributes, applies `ATTR_CMN_RETURNED_ATTRS` / `FSOPT_PACK_INVAL_ATTRS`, optionally reuses kernel UIO buffers, and dispatches to:

- `attr_pack_common()`
- `attr_pack_dir()`
- `attr_pack_file()`
- `attr_pack_common_extended()`

## Common, Directory, File, And Extended Common Packing

`attr_pack_common()` packs names, device IDs, fsids, vnode type/tag, object IDs, times, Finder Info, owner/group/mode/flags, user access, ACL/filesec blobs, UUIDs, file IDs, parent IDs, full paths, added time, and data protection flags. It handles both direct vnode-backed calls and bulk calls where values may already be supplied in `vnode_attr`.

`attr_pack_dir()` packs directory link count, child count, mount status, allocation size, I/O block size, and data length. Mount status reports direct mount points and, under trigger support, mount triggers.

`attr_pack_file()` packs link count, total size, allocation size, I/O block size, device type, data fork size/allocation, and resource fork size/allocation. For non-bulk calls it queries the resource fork through the extended attribute interface and combines resource fork size with data/total size where required.

`attr_pack_common_extended()` treats forkattr bits as extended common attributes when `FSOPT_ATTR_CMN_EXTENDED` is enabled. It packs relative path, private size, link ID, no-firmlink path, real device/fsid, clone ID, extended flags, recursive generation count, attribution tag, and clone refcount.

## Fallback And Compatibility Logic

`vattr_get_alt_data()` handles unsupported filesystem attributes and VFS synthesis. It clears unneeded active bits, derives parent IDs from firmlink or parent vnode state when possible, allows data size/allocation to fall back to total size/allocation, defaults text encoding to Mac Unicode when permitted, and defaults directory link count to `1`.

`calc_varsize()` computes variable-buffer requirements and builds:

- `ATTR_CMN_NAME`
- `ATTR_CMN_FULLPATH`
- `ATTR_CMNEXT_RELPATH`
- `ATTR_CMNEXT_NOFIRMLINKPATH`
- `ATTR_CMN_EXTENDED_SECURITY`

Path construction is delegated to `attrlist_build_path()`, which supports long paths for processes opted into long path support and frees/reallocates buffers as it grows from `MAXPATHLEN` toward `MAXLONGPATHLEN`.

## Public Getattr Entry Points

The file implements:

- `fgetattrlist()`: obtains vnode from fd, copies in attrlist, uses file credential for MAC getattr filtering.
- `getattrlist()`: path-based wrapper around `getattrlistat_internal()` with `AT_FDCWD`.
- `getattrlistat()`: fd-relative path lookup wrapper.
- `getattrlistat_internal()`: performs name lookup with `FSOPT_NOFOLLOW`, `FSOPT_NOFOLLOW_ANY`, and `FSOPT_RESOLVE_BENEATH` handling, then calls `getattrlist_internal()`.

## Bulk Directory Attribute Enumeration

`getattrlistbulk()` implements directory entry plus attribute enumeration. It requires a readable directory fd, validates required bulk attrs, authorizes directory list/search access, tracks enumeration state in `fd_vn_data`, and uses a native filesystem `VNOP_GETATTRLISTBULK` when suitable.

If native bulk support is unavailable or inappropriate, it falls back to `readdirattr()`:

- `refill_fd_direntries()` fills a per-fd directory-entry cache using `vnode_readdir64()` and grows the buffer size up to `FV_DIRBUF_MAX_SIZ` for filesystems needing larger reads.
- `get_direntry()` returns the current cached entry without advancing.
- `direntry_done()` advances to the next cached entry.
- `readdirattr()` skips invalid, `.` and `..` entries, resolves each child without crossing mounts, calls `getattrlist_internal()` with an authoritative name, emits error entries via `get_error_attributes()` when per-child getattr fails, aligns entries to 8 bytes, and updates the UIO offset to the last successful readdir offset.

Bulk mode always enables `FSOPT_ATTR_CMN_EXTENDED` internally and uses `UT_KERN_RAGE_VNODES` while native or fallback enumeration may create transient vnodes.

## Set Attribute Path

`setattrlist_internal()` handles the write side. It validates settable masks, copies in the caller’s attribute buffer, unpacks fixed and referenced fields, authorizes changes, and applies updates through `vnode_setattr()`, extended attributes, HFS boot-info ioctls, or `vfs_setattr()` for volume names.

Supported write-side fields include:

- common times, encoding, Finder Info, owner, group, mode, flags, ACL/filesec, UUIDs, added time, and data protection class;
- volume name through `ATTR_VOL_INFO | ATTR_VOL_NAME`;
- limited file attr handling, with device type changes rejected.

Important ordering logic: when setting both owner write permission removal and Finder Info, Finder Info is written before `vnode_setattr()` so permission changes do not prevent the metadata update.

Public setters are:

- `setattrlist()`: path lookup then set.
- `setattrlistat()`: fd-relative path lookup then set.
- `fsetattrlist()`: fd vnode lookup then set.

They honor no-follow options, resolve-beneath options, and file lease breakage where configured.

## Security And Authorization

The file is tightly integrated with XNU authorization layers:

- `kauth` actions are derived during attrlist parsing.
- `vnode_authorize()` gates reads and writes.
- `vnode_authattr()` computes authorization for attribute mutations.
- `mac_vnode_check_getattrlist`, `mac_vnode_check_getattr`, `mac_mount_check_getattr`, `mac_vnode_check_setattrlist`, and related MAC hooks filter or deny operations when `CONFIG_MACF` is enabled.
- Bulk directory reads perform `mac_vnode_check_readdir()` and may require `KAUTH_VNODE_SEARCH` beyond simple list access depending on requested attrs.
- Swap vnode mutation is restricted outside development/debug kernels.

## Error Handling And ABI Behaviors

Common error outcomes include:

- `EINVAL` for invalid bitmaps, incompatible attr groups, unsupported required attrs without returned-attrs mode, malformed set buffers, or invalid options.
- `ERANGE` for too-small initial result buffers.
- `ENOMEM` for oversized attr buffers or allocation failure.
- `EBADF`, `ENOTDIR`, and lookup errors from fd/path handling.
- `ERESTART` when filesystem type-name reference changes while packing volume attributes.

`ATTR_CMN_RETURNED_ATTRS` lets callers receive a mask of actually returned attributes. `FSOPT_PACK_INVAL_ATTRS` forces every requested field to occupy ABI space while marking only valid fields in the returned mask, preventing uninitialized data by zeroing or defaulting missing values.

## Notable Implementation Details

- The file preserves old Carbon/HFS compatibility semantics, including boot-volume naming, HFS boot info via filesystem-specific ioctls, and resource fork size through xattrs.
- It distinguishes `ATTR_CMN_DEVID` / `ATTR_CMN_FSID` from real device/fsid behavior controlled by `FSOPT_RETURN_REALDEV`.
- It protects fixed-size packing with panic diagnostics when internally computed fixed sizes do not match packed output in non-return-valid mode.
- It supports long path aware processes through larger attr buffers and path construction retry loops.
- It treats forkattr bits as extended common attributes only when explicitly opted in, while rejecting legacy forkattr use in that mode.

## Dependencies

This implementation depends on XNU VFS/vnode primitives, namei lookup, mount/vfs attribute APIs, UIO helpers, kauth/MAC security, xattr helpers, Finder/resource fork naming conventions, FSEvents hooks, file descriptor vnode state, and optional compile-time support for firmlinks, triggers, file leases, and MACF.

## Research Notes

The complete 5000-line source file was read. The file is a central Darwin VFS ABI adapter for attrlist syscalls, with most complexity coming from legacy layout compatibility, unsupported filesystem attribute synthesis, security filtering, directory bulk enumeration state, and the split between volume-level and vnode-level attributes.
