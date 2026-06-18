# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs.h

Internal kernel header for FreeBSD tarfs, a read-only filesystem backed by a tar archive with optional decompression and sparse-file block maps.

Key responsibilities:
- Declares tarfs malloc types, sysctl root, and core forward declarations.
- Defines `struct tarfs_node`, the in-memory node representation for directories, regular files, symlinks, device nodes, FIFOs, and hard-link aliases.
- Stores per-node attributes including inode, type, archive offset, logical/physical sizes, name, owner/group/mode, flags, link count, timestamps, generation, parent, vnode pointer, and block map.
- Defines directory state as an ordered `TAILQ` plus cached readdir cookie/node, symlink target state, device `rdev`, and regular-file hard-link target pointer.
- Defines `struct tarfs_blk` sparse map entries with physical input offset, logical output offset, and length.
- Defines decompression support structures: fixed-size `tarfs_zbuf`, mount-level `tarfs_zio`, zstd state pointer, input/output positions, and compression-frame index.
- Defines `struct tarfs_mount`, holding all nodes, root, backing vnode, VFS mount, inode allocator, I/O sizing, stat counters, archive mtime, and optional decompression vnode.
- Defines tarfs file handles for NFS export support using length, generation, and inode.
- Provides lock macros, tar block sizing/alignment macros, preferred I/O-size tuning constants, reserved inode values, directory cookie constants, and the debug `.tar` znode name.
- Declares node allocation, block-map loading, lookup, read, I/O init/fini/read, buffer read, and file-flag parsing helpers.

Dependencies:
- FreeBSD kernel-only types and facilities: vnodes, mounts, component names, malloc types, sysctls, mutexes, TAILQ, device numbers, file ids, and vnode operation vectors.
- `tarfs_vnodeops` is defined in `tarfs_vnops.c`; I/O and decompression functions are implemented in `tarfs_io.c`; archive parsing and mount operations are in `tarfs_vfsops.c`.

Notable risks:
- `TARFS_ALLNODES_LOCK(tnp)` and unlock macros take a parameter named `tnp` but reference `tmp`; call sites rely on a visible `tmp` variable.
- Hard links are represented through `other` pointers and adjusted link counts, so teardown must avoid double-freeing shared file data.
- Sparse block-map correctness is central to read behavior and `bmap`/readahead hints.
- Reserved inode numbers for root and decompression znode must not collide with allocated archive node inodes.
