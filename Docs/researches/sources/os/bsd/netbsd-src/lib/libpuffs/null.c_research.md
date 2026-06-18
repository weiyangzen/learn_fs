# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/null.c

This file implements a puffs-backed "nullfs" example/library helper that forwards vnode operations to ordinary host filesystem syscalls using paths built by libpuffs. `puffs_null_setops` installs fs and node callbacks for statvfs, file handles, lookup, create, mknod, attributes, fsync, removal, link, rename, directories, symlinks, readdir, read, and write, while using `puffs_genfs_node_reclaim` for reclaim.

The core metadata helper is `makenode`, which applies requested attributes with `processvattr`, creates a `puffs_node`, refreshes attributes from `lstat`, and fills `puffs_newinfo`. `processvattr` maps vnode attributes to `lchown`, `lchmod`, `lutimes`, and regular-file `truncate`. `writeableopen` temporarily chmods a file to owner-write if open for write fails with `EACCES`, then restores the original mode.

Lookup first verifies the backing path with `lstat`, then searches existing puffs nodes by inode using `puffs_pn_nodewalk`; this avoids returning stale removed nodes but is explicitly noted as slow. File-handle support uses `getfh`, strips an 8-byte fhandle header into a kernel fid-like blob, and only supports handles issued while the server is alive by caching copied fid data in `pn_data`.

Directory reads reopen the directory for each request and skip entries by repeated `readdir_r` calls based on the offset, then emits dirent cookies with `PUFFS_STORE_DCOOKIE`. Reads and writes open the file, seek, perform one syscall, and return residual bytes by subtracting bytes transferred from `*buflen`.

Important limitations are documented in comments: attribute updates have no rollback, file handles are not stable across server lifetime, directory offset handling avoids persistent state, and node lookup by inode is linear.
