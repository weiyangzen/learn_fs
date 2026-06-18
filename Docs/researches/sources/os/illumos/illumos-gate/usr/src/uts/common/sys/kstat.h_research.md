# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstat.h

## Purpose
Defines the kernel statistics ABI, `/dev/kstat` ioctls, kstat header structure, data type layouts, flags, snapshot/update semantics, I/O queue accounting helpers, timer statistics, and kernel creation/deletion APIs.

## Main Interfaces
- `kid_t`: unique kstat ID type.
- Ioctls:
  - `KSTAT_IOC_CHAIN_ID`
  - `KSTAT_IOC_READ`
  - `KSTAT_IOC_WRITE`
- `kstat_t`: generic kstat header and kernel-private callbacks.
- 32-bit ABI form under `_SYSCALL32`: `kstat32_t`.
- Kernel locking/callback macros:
  - `KSTAT_ENTER()`
  - `KSTAT_EXIT()`
  - `KSTAT_UPDATE()`
  - `KSTAT_SNAPSHOT()`
- Kstat types:
  - `KSTAT_TYPE_RAW`
  - `KSTAT_TYPE_NAMED`
  - `KSTAT_TYPE_INTR`
  - `KSTAT_TYPE_IO`
  - `KSTAT_TYPE_TIMER`
- Flags:
  - `KSTAT_FLAG_VIRTUAL`
  - `KSTAT_FLAG_VAR_SIZE`
  - `KSTAT_FLAG_WRITABLE`
  - `KSTAT_FLAG_PERSISTENT`
  - `KSTAT_FLAG_DORMANT`
  - `KSTAT_FLAG_INVALID`
  - `KSTAT_FLAG_LONGSTRINGS`
- Data structures:
  - `kstat_named_t`
  - `kstat_intr_t`
  - `kstat_io_t`
  - `kstat_timer_t`
- Kernel APIs:
  - creation/install/delete functions
  - named/timer initialization
  - I/O queue transition helpers
  - timer start/stop helpers
  - zone add/remove/find
  - hold/release by KID or name

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, and under kernel builds `sys/t_lock.h`. Kstats are exposed to userland through `/dev/kstat` while providers initialize and update data in kernel.

## Research Notes
The comments are part of the contract: variable-size kstats must be virtual and locked, snapshots copy data into wired kernel buffers, and long string named kstats require special buffer layout. I/O statistics use accumulated time and length-time products maintained only through helper functions.
