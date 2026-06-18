# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vfsops.c

Read completely: 496 lines.

This implements tmpfs VFS operations and module registration. It initializes/destroys global dirent and node pools, validates mount arguments, computes default memory/node limits, supports `MNT_GETARGS`, handles update mounts, creates the root directory node, sets mount flags and statvfs information, and registers tmpfs vnode operation vectors.

Unmount flushes vnodes, detaches and frees all directory entries, clears vnode pointers, drops root and directory virtual links, frees all nodes, destroys memory accounting, and releases the mount structure. File-handle conversion supports `vptofh` and a linear-list `fhtovp` lookup using node id and generation.

Important interactions: `tmpfs_newvnode` and `tmpfs_loadvnode` are implemented in `tmpfs_subr.c`; FIFO/spec/normal vnode op descriptors are aggregated here. Mount memory accounting uses `tmpfs_mem.c`.

Security/reliability notes: update mounts reject node-limit shrink below current count and memory-limit shrink below current use. `tmpfs_vget` by inode number is unsupported; NFS-style file handles use explicit tmpfs fid data instead.
