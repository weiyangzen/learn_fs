# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fssnap.h

## Role

`fssnap.h` defines the kernel-only backend data structures for UFS-style filesystem snapshots backed by copy-on-write storage. It is the private state contract shared by the snapshot block/character driver and filesystem code.

## Key Interfaces and Data

- Defines snapshot work sizing: `FSSNAP_TASKQ_THREADS`, `FSSNAP_MAX_MEM_CHUNKS`, and `FSSNAP_TASKQ_MAXTASKS`.
- Introduces `chunknumber_t` and conversion macros `dbtocowchunk()` and `cowchunktodb()` that deliberately avoid byte conversion overflow.
- Defines `snapshot_id_t`, including the snapshot list link, enable/disable `krwlock_t`, `cow_info_t` pointer, snapshot number, state flags, and root vnode.
- Defines snapshot state flags: disabled, disabling, block/char open, creating, and delete-on-error. Macros `SID_BUSY()`, `SID_INACTIVE()`, and `SID_AVAILABLE()` encode lifecycle predicates.
- Defines `cow_map_t`, the central translation map: candidate bitmap, translated bitmap, translation table, chunk sizing, backing-file sizing, and write throttling semaphore.
- Defines `cow_map_node_t` for in-memory chunk copies pending writeback.
- Defines `cow_info_t`, tying backing files, task queue, kstats, and `cow_map_t` together.
- Defines `cow_kstat_num` and `COWSTATE_*` numeric state values.

## Dependencies and Use

This header depends on kernel buffer, task queue, and UFS inode declarations. It is guarded by `_KERNEL`; userland sees none of the structures. `fssnap_if.h` layers ioctl and filesystem-operation entry points on top of these types.

## Research Notes

The core design is chunk-granular COW. Candidate chunks are read-only after setup, while translation state is protected by `cmap_rwlock`; `cow_info_t` is mostly immutable after creation except for allocation progress managed atomically in implementation files.
