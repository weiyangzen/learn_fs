# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vops.c

Vnode/VFS adapter layer for SMB filesystem operations. Higher SMB service code is expected to go through `smb_fsop_*`, which then uses these `smb_vop_*` wrappers for local filesystem interaction with SMB-specific normalization.

Initialization allocates a lock-manager sysid and caller context used for range/share locking, sets an ignore PID, initializes CATIA translation tables, and tears them down in `smb_vop_fini`. Basic wrappers cover open, close, read, write, ioctl, zero-copy buffer request/return, fsync, statvfs, and checking for other opens or mappings.

Attribute handling is SMB-aware. `smb_vop_getattr` retrieves extended attributes when `VFSFT_XVATTR` is supported, maps readonly/hidden/system/archive/reparse/offline/sparse and creation time, falls back to mtime as creation time otherwise, and adjusts stream attributes so named streams inherit most metadata from the unnamed stream but use their own size. It also normalizes directories to size/allocation zero and one link, and ensures ordinary files have `FILE_ATTRIBUTE_NORMAL` when no DOS attributes are set. `smb_vop_setattr` masks settable DOS attributes, splits stream size changes from unnamed-stream metadata updates, builds `xvattr_t` when possible, and applies size to the stream vnode with `zone_kcred` when needed.

Name operations wrap lookup/create/remove/link/rename/mkdir/rmdir with case-insensitive flags and optional CATIA name conversion. Lookup handles empty names, `..` at share root, mount-root traversal races, optional returned on-disk names, privilege-based ACL-check skipping for traverse checks, and optional attribute fetch. Create works around filesystems that ignore nonzero size at create by setting size afterward.

Directory enumeration uses `VOP_READDIR` with `edirent_t` support when `VFSFT_DIRENTFLAGS` is available and access-based filtering when requested. Stream helpers map SMB named streams to extended attributes using `SMB_STREAM_PREFIX`, manage xattr directory lookup/creation, and strip/restore on-disk stream prefixes.

ACL helpers read/write either POSIX draft ACLs or ACE ACLs via `VOP_GETSECATTR`/`VOP_SETSECATTR`, detect ACL type through `_PC_ACL_ENABLED`, and compute effective access by probing every relevant ACE or Unix permission bit. `smb_vop_access` adds Windows delete semantics by checking parent `ACE_DELETE_CHILD` and parent list permission for read attributes.

Locking helpers translate SMB share modes into `VOP_SHRLOCK` structures and byte-range locks into mandatory `VOP_FRLOCK` calls when NBMAND is available. Advisory locks are only used when `smb_allow_advisory_locks` permits the dangerous fallback.

CATIA support maps Windows-incompatible UNIX filename characters to Unicode substitutes and back, including create/link/rename/mkdir rejection when reverse conversion would produce `/`. The lookup tables are initialized once and conversion routines preserve original names on decode/space failures.
