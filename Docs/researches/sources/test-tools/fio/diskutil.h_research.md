# sources/test-tools/fio/diskutil.h

Purpose: Declares disk utilization data structures, inline user-count helpers, and feature-gated public APIs.

Important APIs/types: Defines `disk_util_stats`, `disk_util_stat`, `disk_util_agg`, and `disk_util`. Inline helpers `disk_util_mod()`, `disk_util_inc()`, and `disk_util_dec()` mutate active-user counts for a device and its slaves. `DISK_UTIL_MSEC` sets the polling interval. `disk_list` is extern.

Control flow: Jobs call increment/decrement helpers around active device use; the helper thread consumes public update/prune/setup/init APIs when `FIO_HAVE_DISK_UTIL` is enabled. Disabled builds compile to no-ops, with `update_io_ticks()` returning `helper_should_exit()`.

State/persistence: Per-device state stores sysfs root, stat path, major/minor, accumulated and last counters, aggregate fields, slave lists, timestamp, lock, and users.

Dependencies/integration: Requires fio helper thread, semaphores, flist, and fio's IEEE754 wrapper for aggregated utilization.

Risks: Inline mutation of slave users happens while holding only the master lock, not each slave lock. Feature-gated no-ops mean callers must tolerate absence of disk utilization.

Test signals: Compile both enabled and disabled configurations; validate user counts and slave propagation in software RAID/device-mapper setups.
