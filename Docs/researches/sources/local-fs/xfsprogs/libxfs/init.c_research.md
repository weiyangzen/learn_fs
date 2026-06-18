# File Research: sources/local-fs/xfsprogs/libxfs/init.c

Core libxfs initialization, mount setup, buffer-target setup, and teardown.

Key responsibilities:
- Opens data, log, and realtime devices with readonly/direct/exclusive/create semantics.
- Checks mounted/writable device state according to libxfs flags.
- Initializes global runtime support: page shift, ondisk structure checks, xmbuf, RCU, radix tree, directory startup, and slab-like caches.
- Creates data/log/realtime buffer targets and cache objects.
- Supports write-failure injection through `LIBXFS_DEBUG_WRITE_CRASH`.
- Initializes mount geometry, feature flags, btree maxlevels, DA geometry, transaction reservations, per-AG structures, realtime fields, rtgroups, and metadata directory root.
- Performs device size checks unless debugger mode allows continuing.
- Flushes dirty buffers and device write caches, reporting corrupt/lost writes.
- Unmounts and destroys libxfs global resources.

Important behavior:
- Tools can run with fake device numbers for regular files.
- Realtime setup validates incompatibilities such as reflink with realtime extent size > 1.
- Extremely high AG or rtgroup counts are guarded by read probes and can be limited in debugger mode.
- V1 inodes and V1 directories are refused.
- `libxfs_umount` purges the buffer cache before flushing devices and freeing perag/rtgroup state.

Dependencies:
- Uses platform/device helpers, cache, kmem caches, libxfs mount/sb/geometry, transactions, btrees, metadir, realtime, xfile, and buffer APIs.

Notable risks:
- Many paths call `exit(1)` or `abort()` on fatal setup failures.
- Device/mount safety depends on platform mounted/writable detection.
- Teardown order is important because buffers, per-AGs, rtgroups, and metadata inodes reference each other.
