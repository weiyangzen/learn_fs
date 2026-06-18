# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_vnops.c

Tmpfs vnode operations for regular file I/O, directory namespace operations, extended attributes, VM paging, mmap, truncation, locking, fids, and pathconf.

Key responsibilities:
- Defines `tmp_vnodeops_template` covering open/close/read/write/ioctl/getattr/setattr/access/lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink/fsync/inactive/fid/rwlock/rwunlock/seek/space/getpage/putpage/map/addmap/delmap/pathconf/vnevent.
- Denies swap activation on tmpfs files in `tmp_open()` when `VISSWAP` is set.
- Implements regular-file writes in `wrtmp()`: mandatory lock checks, file-size/resource limits, swap reservation, anon slot allocation, segmap/VPM data copy, zeroing for partial new pages, size update/rollback, setuid/setgid clearing, and timestamp updates.
- Implements regular-file reads in `rdtmp()`: mandatory lock checks, EOF clipping, segmap/VPM copy, and access-time updates.
- Implements attributes and permissions through `tmp_getattr()`, `tmp_setattr()`, and `tmp_access()`, including root ownership refresh from covered vnode, policy checks, and truncate-on-size changes.
- Implements namespace VOPs on top of `tmp_dir.c`: lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, and readlink.
- Implements xattr-directory lookup/creation for `LOOKUP_XATTR`, with mode derivation and hidden xattr tmpnode setup.
- Wraps special-device tmpfs nodes with `specvp()` on lookup/create when needed.
- Implements `tmp_inactive()` to free unlinked tmpnodes, truncate remaining file data, remove xattr directories, unlink from mount list, destroy locks, free vnode, and free tmpnode memory.
- Implements VM fill/writeback via `tmp_getpage()`, `tmp_getapage()`, `tmp_putpage()`, and `tmp_putapage()`, using anon slots and physical swap backing only when pages must be paged out.
- Implements mmap through `tmp_map()` with `segvn_create`, while `tmp_addmap()` and `tmp_delmap()` are no-ops.
- Implements `F_FREESP` through `tmp_space()` and `tmp_freesp()`, with mandatory lock checks and `tmpnode_trunc()`.
- Implements fids (`tmp_fid()`), seek bounds, rwlock wrappers, and pathconf values for xattrs, system attributes, and timestamp resolution.

Dependencies:
- Uses tmpfs directory helpers (`tdirlookup`, `tdirenter`, `tdirdelete`, `tdirinit`, `tdirtrunc`) and tmpnode helpers (`tmp_resv`, `tmpnode_growmap`, `tmpnode_trunc`, `tmpnode_init`).
- Uses anon/swap helpers `anon_get_ptr`, `anon_set_ptr`, `anon_alloc`, `non_anon`, `swap_getphysname`, and `swap_newphysname`.
- Uses VM helpers `segmap`, `vpm`, `pvn_getpages`, `pvn_write_kluster`, `VOP_PAGEIO`, and page-cache lookup/writeback routines.
- Uses vnode event notification helpers for create/remove/link/rename/rmdir/truncate.

Concurrency and locking:
- Higher layers call `tmp_rwlock()`/`tmp_rwunlock()` around read/write-style operations; internal paths use `tn_rwlock` and `tn_contents`.
- Read/write drop `tn_contents` around segmap/VPM copying to avoid deadlocks when page faults re-enter tmpfs.
- `tmp_getpage()` upgrades `tn_contents` from reader to writer when it must instantiate anon slots for holes.
- `tmp_putpage()` avoids blocking pageout on `tn_contents`; pageout uses `rw_tryenter()` and returns `ENOMEM` if it cannot acquire the lock.
- `tmp_rename()` serializes mount-wide renames through `tm_renamelck`.

Notable risks:
- Tmpfs reserves swap for file growth before pages necessarily exist; holes are materialized later during getpage/write paths.
- `tmp_putpage()` normally does no I/O except pageout/free, invalidate, or explicit dontneed paths.
- `tmp_inactive()` has a retry loop because pages or anon slots can keep a vnode discoverable after link count reaches zero.
- Xattr directories are lazily created by lookup and have special restrictions on contained object types and link counts.
