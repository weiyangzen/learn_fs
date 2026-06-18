# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_send.h

Read status: complete, 53 lines.

Purpose: send-side DMU stream interface.

Key APIs:
- `dmu_send()` sends a dataset snapshot stream by name, optionally incremental from another snapshot, with embedded/large-block/compressed/raw stream options and resume object/offset support.
- `dmu_send_estimate()` and `dmu_send_estimate_from_txg()` estimate stream size.
- `dmu_send_obj()` sends by pool and snapshot object ids.

Dependencies: integer types, SPA, vnode, dataset and replay-record forward declarations.

Research notes:
- Complements internal `dmu_sendarg_t` in `dmu_impl.h`.
- Supports resumable send and feature-controlled stream formats.
