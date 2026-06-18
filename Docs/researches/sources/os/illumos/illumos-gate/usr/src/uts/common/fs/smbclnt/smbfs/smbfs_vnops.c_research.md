# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vnops.c

## Purpose
SMBFS vnode operation implementation. It maps Solaris vnode operations to SMB client operations, VM/page-cache behavior, namespace changes, local access checks, mmap handling, locks, pathconf, and ACL hooks.

## Core Themes
- Enforces owning-zone checks on nearly every operation.
- Treats dead or unmounted mounts as `EIO`.
- Uses local Unix-mode checks based on mount uid/gid/mode, while SMB server enforces remote credentials.
- Reuses SMB FIDs across opens when rights and generation are compatible.
- Supports both direct I/O and VM-backed cached I/O.
- Implements XATTR/named-stream support through fake XATTR directories.
- Many unsupported Unix features return `ENOSYS`: hard links, symlinks, readlink, fid, realvp.

## Open/Close and FID Lifecycle
- `smbfs_open(...)`
  - Allows regular files and directories.
  - Serializes FID/directory-sequence state with `r_lkserlock`.
  - For directories, opens a find context and tracks `n_dirrefs`.
  - For regular files, reuses `n_fid` when rights are sufficient and VC generation matches.
  - Opens with read-control/read-attributes plus requested read/write rights.
  - Saves credentials used for open and records first-open vnode type in `n_ovtype`.
- `smbfs_close(...)`
  - Cleans local locks when mounted with local locking.
  - On last close, writes dirty pages for write opens.
  - Calls `smbfs_rele_fid(...)`.
- `smbfs_rele_fid(...)`
  - Closes directory find contexts or releases file FIDs when reference counts reach zero.
  - Clears cached credentials and invalidates changed attributes.

## Read/Write and Page Cache
- `smbfs_read(...)`
  - Validates open FID, type, offsets, EOF, and caches.
  - Uses direct `smb_rwuio` if `VNOCACHE`, direct I/O, or mount direct I/O conditions apply.
  - Otherwise uses segmap/VPM paths.
- `smbfs_write(...)`
  - Handles append, sync flags, file-size limit enforcement, stale-node errors, direct I/O, and segmap writes.
  - Marks `NFLUSHWIRE`, `NATTRCHANGED`, and `RDIRTY` as appropriate.
- `smbfs_writenp(...)`
  - Kernel-only writer helper that creates/touches pages and updates `r_size`.
  - Uses `RMODINPROGRESS` to coordinate with pageout.
- `smbfs_bio(...)`
  - Performs page I/O via `smb_rwuio`.
  - Handles EOF clipping, zero-fill beyond EOF for reads, sync flush after writes, and error propagation.
- `smbfs_getpage(...)`, `smbfs_getapage(...)`
  - Kernel VM page-in support, including cache validation and EOF/stale retry handling.
- `smbfs_putpage(...)`, `smbfs_putapage(...)`
  - Kernel page writeback support.
  - Handles `ROUTOFSPACE`, forced invalidation, clustering, `RMODINPROGRESS`, and retry/invalidating behavior on out-of-space style errors.
- `smbfs_invalidate_pages(...)`
  - Invalidates cached pages from an offset, coordinating with `RTRUNCATE`.

## Attributes, Access, and ACLs
- `smbfs_getattr(...)`
  - Returns hint-only cached size/fsid/rdev when allowed.
  - Flushes dirty pages before mtime-sensitive getattr.
  - Delegates actual attribute fetch to `smbfsgetattr`.
- `smbfs_setattr(...)` / `smbfssetattr(...)`
  - Performs Solaris policy checks using mount owner semantics.
  - Supports size, atime, mtime, and DOS attributes from extensible attrs.
  - Uses temporary SMB opens when handle-based setting is needed.
  - XATTR directories ignore setattr; XATTR files only allow size changes.
- `xvattr_to_dosattr(...)`
  - Maps archive/system/readonly/hidden extensible attributes to SMB DOS attributes.
- `smbfs_access_rwx(...)`
  - Implements local access checks from mount uid/gid/file mode/dir mode.
- `smbfs_getsecattr(...)` / `smbfs_setsecattr(...)`
  - Use SMB ACL implementation when `SMI_ACL` is enabled.
  - Falls back to fabricated ACLs for get when ACL support is unavailable.

## Namespace Operations
- `smbfs_lookup(...)` / `smbfslookup(...)`
  - Handles `LOOKUP_XATTR`, empty name, `.`, `..`, illegal characters, cache lookup, and over-the-wire lookup.
  - For `..`, trims cached remote paths rather than going over the wire.
  - Prunes caches when remote lookup indicates a directory was removed/renamed.
- `smbfslookup_cache(...)`
  - Reclaims valid nodes from the path-keyed smbnode cache without an OTW lookup.
- `smbfs_create(...)`
  - Handles existing-file open/truncate and new creation via SMB create dispositions.
  - Performs local access checks for both directory write and requested file access.
  - For XATTR directories, passes xattr mode to SMB create.
- `smbfs_remove(...)` / `smbfsremove(...)`
  - Opens target with delete access, optionally renames locally open files to temporary names, sets delete-on-close, and removes node from hash on success.
  - Uses delete-on-close to fit SMB semantics while approximating Unix unlink expectations.
- `smbfs_rename(...)` / `smbfsrename(...)`
  - Locks source and target directories in address order to avoid deadlock.
  - Removes existing file targets before rename when needed.
  - Uses a temporary delete-access handle for SMB rename.
  - Prunes source subtree caches on success.
- `smbfs_mkdir(...)`
  - Creates remote directory, re-looks it up, touches parent attrs, returns vnode.
- `smbfs_rmdir(...)`
  - Validates directory, mountpoint, root/current-dir conditions, then reuses `smbfsremove`.
- `smbfs_readdir(...)` / `smbfs_readvdir(...)`
  - Serializes directory enumeration with `r_lkserlock`.
  - Synthesizes `.` and `..`.
  - Uses SMB findnext, assigns cookie-like offsets, and optionally pre-populates node cache via `smbfs_fastlookup`.
  - Keeps find context open until close so EOF reads remain stable.

## mmap and Locks
- `smbfs_map(...)`
  - Validates open FID, type, offsets, mandatory lock interactions, and cacheability.
  - Uses `as_map` with `segvn_create`.
- `smbfs_addmap(...)`
  - Increments `r_mapcnt` and keeps SMB FID referenced while mapped.
- `smbfs_delmap(...)` / `smbfs_delmap_async(...)`
  - Queues async work to flush mapped dirty ranges and release FID refs when map count reaches zero.
- `smbfs_frlock(...)` / `smbfs_shrlock(...)`
  - Use local filesystem lock helpers only when `SMI_LLOCK` is set; otherwise return `ENOSYS`.

## Miscellaneous Vnode Ops
- `smbfs_ioctl(...)`
  - Supports `_FIOFFS`, direct I/O toggle, and raw SMB security descriptor get/set ioctls.
- `smbfs_fsync(...)`
  - Writes dirty pages and sends SMB flush when needed.
- `smbfs_inactive(...)`
  - Waits for async activity, flushes/invalidates pages, then calls `smbfs_addfree`.
- `smbfs_seek(...)`
  - Permits directory cookie seeks and rejects negative file offsets.
- `smbfs_space(...)`
  - Implements truncate via `F_FREESP` with zero length.
- `smbfs_pathconf(...)`
  - Reports file size bits, link max, ACL mode, symlink max, XATTR existence, system attribute support, and timestamp resolution.

## Vnode Op Table
Registers implementations for open, close, read, write, ioctl, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, fid, rwlock/rwunlock, seek, frlock, space, realvp, kernel page/mmap ops, pathconf, security attrs, and share locks.
