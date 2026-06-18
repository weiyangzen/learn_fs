# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock_impl.h

This private header defines the on-disk uberblock layout and MMP field encoding.

Core definitions:
- `UBERBLOCK_MAGIC`, `UBERBLOCK_SHIFT`, and `MMP_MAGIC` identify uberblocks and MMP heartbeat data.
- MMP valid-bit macros and getters/setters encode write interval, sequence, and fail intervals into `ub_mmp_config`.
- `struct uberblock` stores magic, SPA version, synced txg, vdev guid sum, timestamp, MOS root block pointer, writing software version, MMP magic/delay/config, and checkpoint TXG.

Risk-sensitive invariants:
- `ub_magic` and `ub_version` must remain the first two fields so version/magic can be read before compatibility is known.
- `ub_mmp_delay == 0` with valid MMP magic means MMP is off.
- `ub_checkpoint_txg` marks checkpointed uberblocks and determines claim behavior when rewinding to a checkpoint.
- MMP config bit widths cap interval and sequence/fail values; setters mask values into the persistent layout.
