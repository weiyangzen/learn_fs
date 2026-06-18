# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_impl.h

Read status: complete, 303 lines.

Purpose: private DMU implementation definitions, especially lock-order documentation, xuio stats, send-stream aggregation state, and internal object helpers.

Key contents:
- Large lock-order comment documents ordering and protected fields across ARC, bplist, refcount, txg, zfetch, objset, dnode, dbuf, dsl_dir, dsl_dataset, dirty records, and pool config locks.
- `dmu_xuio_t` tracks extended-uio ARC buffers and iovec state.
- `xuio_stats_t` exposes loaned/copy/no-copy read/write buffer stats.
- `dmu_pendop_t` tracks pending aggregated send stream operations.
- `dmu_sendarg_t` stores state for send-stream generation, including output vnode/fd/off, objset, checksum, GUID/TXG range, pending free/freeobjects aggregation, feature flags, resume state, and begin/end flags.
- Internal helpers: `dmu_object_zapify()`, `dmu_object_free_zapified()`, `dmu_buf_hold_noread()`.

Dependencies: txg internals, ZIO, dnode, ZFS context/ioctl, DMU types.

Research notes:
- The lock-order section is critical when analyzing deadlock risks in DMU/dbuf/dnode/DSL code.
- Send stream internals here complement the public declarations in `dmu_send.h` and `dmu.h`.
