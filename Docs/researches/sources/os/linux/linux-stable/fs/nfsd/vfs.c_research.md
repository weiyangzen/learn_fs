# File Research: sources/os/linux/linux-stable/fs/nfsd/vfs.c

Purpose: implements the NFSD VFS helper layer. It maps Linux VFS operations and errnos into NFS protocol behavior for lookup, mount/export crossing, attributes, permissions, open, read, write, commit, create, link, rename, unlink, readdir, statfs, xattrs, NFSv4 clone/fallocate, and metadata durability.

Key structures and state:
- Global tunables select read/write cache behavior: `nfsd_disable_splice_read`, `nfsd_io_cache_read`, and `nfsd_io_cache_write`.
- `nfserrno()` maps negative Linux errnos to network-endian NFS status values and warns on unexpected codes.
- `struct accessmap` maps NFS ACCESS bits to internal `NFSD_MAY_*` permission checks for regular files, directories, and special files.
- Direct-write support uses `struct nfsd_write_dio_seg` to split writes into prefix, aligned direct-I/O middle, and suffix segments.
- Readdir buffering uses `struct buffered_dirent` and `struct readdir_data` to decouple `iterate_dir()` from later encoding/lookup work.

Major logic:
- Lookup helpers handle `.`/`..`, parent export lookup, `NOHIDE`, NFSv4 pseudo-root behavior, junction xattrs, automount following, and `CROSSMOUNT`.
- `nfsd_setattr()` sanitizes mode/ownership changes, handles size changes separately, honors ctime guard checks, waits once for delegation return on `-EAGAIN`, applies labels/POSIX ACLs, fills weak cache consistency attrs, and commits metadata for sync exports.
- NFSv4 helpers detect junction xattrs, run `vfs_clone_file_range()` with optional sync/writeback verification, cap copy-file-range chunks to 4 MiB, and call `vfs_fallocate()`.
- `nfsd_access()` computes supported and allowed access masks by probing `nfsd_permission()` and treating denial statuses as ordinary ACCESS false bits.
- Open paths verify filehandles, optionally break leases, honor owner override for regular files after protocol-level open, retry on `-EOPENSTALE`, and expose a filecache-oriented verified open helper.
- Read paths choose splice when safe, otherwise iterator reads; direct reads expand to filesystem alignment and trim the returned payload back to the requested range.
- Write paths convert XDR payloads to bvecs, choose buffered/direct/dontcache operation, set sync flags from NFS stable mode and export sync policy, manage write verifier resets on durable-storage errors, apply local-throttle handling for localhost writes, and update stats/fsnotify.
- Commit converts NFS offset/count to a safe `vfs_fsync_range()` span, checks writeback errors since request start, and returns/reset write verifiers correctly.
- Create, symlink, link, rename, and unlink wrap VFS operations with write access, WCC pre/post attrs, metadata commits, special NFS status translation for busy open files, delegation-return retry, and filecache close-before-unlink/rename support.
- Readdir opens a private directory file, sets 32/64-bit cookie mode, seeks to the requested offset, buffers one page of dirents, and invokes the protocol-specific filldir callback.
- NFSv4 xattr helpers implement get/list/set/remove with permission checks, inode locking, probe-then-allocate reads, `XATTR_LIST_MAX` handling, WCC attrs for modifications, and xattr-specific errno mapping.
- `nfsd_permission()` applies export/mount read-only checks, immutable/append restrictions, owner override, ordinary inode permission checks, and read-if-exec fallback.

Concurrency and lifetime:
- Filehandle operations rely on `fh_verify`, `fh_want_write`, `fh_drop_write`, `fh_fill_pre_attrs`, and `fh_fill_post_attrs`.
- Attribute, xattr, rename, and unlink paths use inode or VFS directory operation locking as appropriate.
- Delegation conflicts are retried once in setattr, rename, and unlink via `nfsd_wait_for_delegreturn()`.
- Filecache entries acquired by `nfsd_file_acquire_gc()` are released with `nfsd_file_put()`.
- `nfsd_filp_close()` performs synchronous final `fput` to prevent nfsd from queuing unbounded asynchronous close work.
- Readdir deliberately avoids `file->f_pos_lock` because the opened file is private to the request.

Important dependencies:
- Uses core VFS APIs: lookup, dentry open, notify_change, file range clone/copy, fallocate, read/write iterators, splice, fsync, statfs, xattrs, link/rename/unlink/mkdir/mknod/symlink, ACLs, security labels, and inode permissions.
- Integrates with NFSD export/filehandle logic, filecache, stats, write verifier state, NFSv3/v4 XDR structs, NFSv4 state/callback semantics, and tracepoints.
- Uses export operation flags such as `EXPORT_OP_REMOTE_FS` and `EXPORT_OP_CLOSE_BEFORE_UNLINK`.

Risk/edge cases:
- Write verifier reset behavior is subtle: some errors imply unstable durable storage and others do not.
- Splice reads are disabled for GSS integrity/privacy because page contents can change after MIC calculation.
- Direct I/O paths depend on exported DIO alignment attributes and fall back or report server fault on unexpected alignment failure.
- Rename is constrained to the same exported mount and export root.
- Xattr list may report `TOOSMALL` or `XATTR2BIG` because VFS/filesystem limits do not line up cleanly with NFSv4 xattr encoding.
