# File Research: sources/teaching/os161/kern/fs/sfs/sfs_vnops.c

Implements user-visible SFS vnode operations for files and the root directory.

File operations:
- `sfs_read` and `sfs_write` validate `uio_rw`, take the VFS biglock, and delegate to `sfs_io`.
- `sfs_stat` fills size, mode, link count, and zeroes unsupported fields.
- `sfs_gettype` maps SFS inode type to `S_IFREG` or `S_IFDIR`.
- `sfs_fsync` syncs the inode.
- `sfs_truncate` delegates to `sfs_itrunc`.
- `sfs_mmap` returns `ENOSYS`.

Directory/name operations:
- `sfs_eachopendir` rejects write/RDWR/append opens on directories.
- `sfs_creat` opens existing names unless `excl`, otherwise creates a file object, links it into the directory, and increments link count.
- `sfs_link` creates hard links to non-directory files and increments link count.
- `sfs_remove` looks up a file, clears its directory entry, decrements link count, and drops the lookup ref.
- `sfs_rename` assumes same root directory and no subdirectories, creates the new link then removes the old link, with cleanup/panic if recovery fails.
- `sfs_lookup` and `sfs_lookparent` only support flat namespace semantics rooted at the directory vnode.
- `sfs_namefile` returns an empty suffix for the root directory.

Ops tables:
- `sfs_fileops` enables file read/write/stat/fsync/truncate and rejects directory-only ops.
- `sfs_dirops` enables create/link/remove/rename/lookup/lookparent/namefile and rejects file data I/O.

Notable limitations:
- No subdirectories, symlinks, mkdir/rmdir, getdirentry, or mmap implementation.
- Permissions are mostly ignored.
