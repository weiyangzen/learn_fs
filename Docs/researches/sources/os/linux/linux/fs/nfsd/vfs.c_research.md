# File Research: sources/os/linux/linux/fs/nfsd/vfs.c

`vfs.c` implements NFSD’s bridge from NFS protocol operations to Linux VFS operations. It handles NFS-specific permission semantics, filehandle/export traversal, metadata updates, file open/read/write/commit paths, namespace mutations, directory iteration, stats, xattrs, and case-folding queries.

Key responsibilities:
- Error conversion: `nfserrno()` maps negative Linux errnos to network-order NFS status values and warns on unexpected errors.
- Lookup and mount traversal: `nfsd_cross_mnt()`, `follow_to_parent()`, `nfsd_lookup_parent()`, `nfsd_mountpoint()`, `nfsd_lookup_dentry()`, and `nfsd_lookup()` implement export-aware component lookup, parent lookup, V4ROOT behavior, junction detection, crossmount/nohide semantics, and filehandle composition.
- Attribute changes: `nfsd_setattr()` sanitizes attrs, handles guard time, splits size changes from other changes, retries delegation conflicts, applies security labels and POSIX ACLs, fills weak cache consistency attrs, and commits sync exports.
- NFSv4 helpers: `nfsd4_is_junction()` detects trusted junction xattrs; `nfsd4_clone_file_range()`, `nfsd_copy_file_range()`, and `nfsd4_vfs_fallocate()` implement v4.2 clone/copy/allocate paths with verifier reset on durable-storage errors.
- Access/open: access maps translate NFSv3/v4 ACCESS bits to `NFSD_MAY_*`; `nfsd_open_break_lease()`, `__nfsd_open()`, `nfsd_open()`, and `nfsd_open_verified()` enforce permissions, leases, append-only checks, stale-open retry, and security post-open hooks.
- Reads: supports splice reads when safe, iterator reads otherwise, and aligned direct reads when configured and possible. GSS integrity/privacy disables splice to avoid reply MIC races.
- Writes: `nfsd_vfs_write()` handles stable/unstable writes, direct/dontcache/buffered modes, write verifier copying/reset, local throttling, writeback error checks, fsnotify, stats, and NFSv2 write-gather behavior.
- Commit: `nfsd_commit()` syncs requested byte ranges and returns/reset write verifiers according to export sync policy.
- Namespace mutation: create, symlink, link, rename, unlink all fill pre/post attrs, acquire write access, use VFS helpers, commit metadata, and translate NFSv4 object-open busy errors specially.
- Readdir: buffers directory entries into a page to avoid lookup recursion/deadlocks from filldir callbacks, then feeds protocol encoders.
- Xattrs: v4 get/list/set/remove xattr helpers use VFS xattr APIs, inode locking, size probing/allocation, WCC attrs, and special xattr error mapping.
- Permissions: `nfsd_permission()` layers export read-only checks, immutable/append handling, owner override, local device access quirks, and inode permission checks.
- Case info: `nfsd_get_case_info()` probes `vfs_fileattr_get()` under kernel credentials and reports POSIX defaults when unsupported.

Notable dependencies include `filecache.h`, `nfsfh.h`, `export.h`, `xdr3.h`, `xdr4.h`, Linux VFS, xattr, fsnotify, writeback, security, and SUNRPC XDR support. The file is heavily instrumented by `trace.h`.
