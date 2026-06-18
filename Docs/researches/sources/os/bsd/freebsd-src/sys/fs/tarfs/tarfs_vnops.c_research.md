# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vnops.c

Tarfs vnode operation implementation for read-only archive nodes, including lookup, readdir, regular reads, symlink reads, buffer strategy, file handles, and attributes.

Key responsibilities:
- Registers `tarfs_vnodeops` with access, bmap, cached lookup, open, close, getattr, read, readdir, readlink, reclaim, strategy, print, and vptofh operations.
- Allows opening regular files and directories, creates VM objects sized to the tarfs node, and rejects other vnode types.
- Enforces read-only semantics by rejecting writes to regular files, directories, and symlinks while using `vaccess()` for ordinary permission checks.
- Implements `bmap()` for logical block mapping and run-ahead/run-behind hints based on sparse block extents and holes.
- Synthesizes vnode attributes from `struct tarfs_node`, including fileid, generation, flags, device number, rounded physical byte count, and timestamps.
- Implements cached lookup for `.`, `..`, ordinary entries, and debug-only root `.tar` znode access; non-last path components must be directories or symlinks.
- Uses `VFS_VGET()` and `vn_vget_ino()` to instantiate lookup targets and populates the namecache when allowed.
- Generates `.` and `..` directory entries, then iterates child `TAILQ` entries using inode cookies and per-directory last-cookie cache.
- Supports NFS directory cookies by returning an array of next offsets that matches emitted entries.
- Reads regular files through `tarfs_read_file()` until EOF or no progress, clipping reads to node logical size.
- Reads symlinks directly from the immutable stored link target.
- Reclaims vnodes by removing them from the VFS hash and clearing the node-vnode backpointer.
- Implements buffer strategy reads by constructing a kernel `uio`, clipping to EOF, and calling `tarfs_read_file()`.
- Encodes file handles using inode and generation.

Dependencies:
- FreeBSD vnode operation framework, namecache, `struct dirent`, UIO, buffer strategy, vnode hash, FIFO print helper, and VFS inode lookup.
- Tarfs node tree, block maps, directory cookies, sparse read helper, and file-handle structure.

Notable risks:
- Directory cookies are inode numbers plus reserved values; correctness depends on stable node inodes during mount lifetime.
- `tarfs_readdir()` uses a per-directory single-entry cache and assumes coherent directory traversal under vnode locking.
- `bmap()` and strategy must handle holes consistently with `tarfs_read_file()` zero-fill behavior.
- The debug-only `.tar` znode path exposes the decompressed archive stream at the root when `TARFS_DEBUG` is enabled.
