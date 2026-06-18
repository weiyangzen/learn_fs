# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs.h

Read completely: 350 lines.

This is tmpfs’s main internal data-model header. It defines `tmpfs_dirent_t` for directory entries, `tmpfs_node_t` for inode-like nodes, and `tmpfs_mount_t` for per-mount memory/node accounting and node lists. Nodes store common attributes, timestamps guarded by `tn_timelock`, lockf state, vnode association, link/hold counts, and type-specific data for devices, directories, symlinks, and regular-file UVM anonymous objects.

The header also defines directory-cookie constants, whiteout/generation-bit macros, timestamp-update flags, NFS fid format, conversion helpers from VFS/vnode to tmpfs structures, and prototypes for tmpfs subroutines and memory-accounting helpers.

Important interactions: consumed by all tmpfs implementation files. `tmpfs_vfsops.c` owns mount creation/destruction; `tmpfs_subr.c` owns node/dirent lifecycle and resize logic; `tmpfs_vnops.c` owns vnode behavior.

Security/reliability notes: explicitly kernel/private except for `_KMEMUSER`. Correctness depends on vnode locks protecting most node and dirent fields, with separate locks for mount accounting and timestamp fields.
