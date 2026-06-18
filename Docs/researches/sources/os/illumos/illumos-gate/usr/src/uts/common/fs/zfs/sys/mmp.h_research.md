# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/mmp.h

This header declares ZFS Multi-Modifier Protection state and tunables. MMP periodically writes heartbeat uberblocks so imports can detect an active pool on another host.

Core definitions:
- Tunables and bounds include `MMP_MIN_INTERVAL`, defaults for interval/import/fail intervals, safety factor, and normalization macros for minimum write/fail intervals.
- `mmp_thread_t` stores thread/CV state, I/O lock, last successful write time, delay estimate, last written uberblock copy, root zio, kstat sequence, skip error, last leaf, leaf-list generation, and sub-second sequence.
- Lifecycle APIs cover `mmp_init()`, `mmp_fini()`, `mmp_thread_start()`, `mmp_thread_stop()`, `mmp_update_uberblock()`, and `mmp_signal_all_threads()`.
- Global tunables are `zfs_multihost_interval`, `zfs_multihost_fail_intervals`, and `zfs_multihost_import_intervals`.

Risk-sensitive invariants:
- Delay, sequence, and last-leaf fields are protected by `mmp_io_lock`; thread management fields are protected by `mmp_thread_lock`.
- MMP writes are based on the last synced uberblock and are meaningful only with the uberblock MMP fields in `uberblock_impl.h`.
- Import safety depends on conservative interval/fail-interval validation and visible heartbeat progress on writable leaf vdevs.
