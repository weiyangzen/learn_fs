# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vfsops.c

Tarfs VFS mount, unmount, archive parser, vnode lookup by inode, file-handle conversion, and statfs implementation.

Key responsibilities:
- Defines POSIX ustar header layout and validates that it is exactly one 512-byte tar block.
- Defines tar type flags, ustar/GNU magic constants, default directory mode, mount options, malloc types, and read-only VFS registration.
- Parses tar numeric fields as signed octal or base-256 two's complement values.
- Verifies tar headers using both standard unsigned and legacy signed checksum calculations.
- Resolves archive paths in the in-memory node tree, optionally creating missing ancestor directories while rejecting invalid `..` traversal above root.
- Frees complete mount state by walking all nodes, finalizing I/O/decompression, deleting the inode allocator, clearing `mnt_data`, and freeing the mount object.
- Parses archive entries in `tarfs_alloc_one()`, including POSIX extended headers, path/linkpath/size overrides, GNU sparse metadata, SCHILY file flags, prefix/name concatenation, hard links, symlinks, device nodes, directories, and regular files.
- Rejects unsupported or malformed formats, including GNU tar magic, invalid checksums, invalid numeric fields, duplicate non-directory entries, unsupported entry types, and inconsistent sparse metadata.
- Allocates mount state from a regular backing vnode, initializes I/O/decompression, creates the root node, then walks all archive headers to populate the tree.
- Implements `tarfs_mount()` with `from`, optional display name `as`, root uid/gid/mode overrides for privileged callers, optional `verify` open flag, source vnode open/close, permission checks, read-only/local mount flags, fsid assignment, and mounted-from string.
- Implements forced/non-forced unmount using `vflush()`, source vnode close, and mount cleanup.
- Implements root vnode lookup through `VFS_VGET()` and marks it `VV_ROOT`.
- Reports `statfs` data from archive block count, preferred I/O size, node count, and zero free space/files.
- Implements `tarfs_vget()` using `vfs_hash_get()`/`vfs_hash_insert()`, all-node inode lookup, znode special case, vnode construction, mount queue insertion, and tarfs vnode op assignment.
- Implements NFS export file-handle conversion through inode and generation checks.

Dependencies:
- FreeBSD VFS, vnode, namei, sbuf, mount option, privilege, GEOM/VFS, malloc, mutex, UIO, stat, and file open/close infrastructure.
- Tarfs node/I/O helpers and `tarfs_vnodeops`.

Notable risks:
- Archive parsing is intentionally strict; many non-POSIX or GNU tar cases return `EINVAL`/`EFTYPE`.
- Extended header parsing mutates the header buffer by writing NUL terminators into line/key separators.
- Hard links are only accepted to existing regular file nodes that are not themselves hard-link aliases.
- The mount parser unlocks the backing vnode inside `tarfs_alloc_mount()` and later relies on caller cleanup paths knowing whether it is locked.
- `tarfs_vget()` linearly scans all nodes on vnode cache miss, which is simple but can be costly for large archives.
- `tarfs_fhtovp()` rejects stale handles by checking inode range, generation, mode, and link count.
