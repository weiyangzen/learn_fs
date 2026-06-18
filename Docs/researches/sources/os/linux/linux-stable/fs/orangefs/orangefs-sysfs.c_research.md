# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.c

## Scope

This file implements OrangeFS sysfs controls and counters under `/sys/fs/orangefs`.

## APIs Covered

- Attribute dispatch: `orangefs_attr_show()`, `orangefs_attr_store()`, `orangefs_sysfs_ops`.
- Local integer attributes: `sysfs_int_show()`, `sysfs_int_store()`.
- Daemon-backed attributes: `sysfs_service_op_show()`, `sysfs_service_op_store()`.
- Kobject lifecycle: `orangefs_sysfs_init()`, `orangefs_sysfs_exit()`.

## Control Flow And Behavior

- Top-level integer attributes expose and update kernel-side `op_timeout_secs`, `slot_timeout_secs`, cache timeout, dcache timeout, and getattr timeout.
- Stats kobject exposes kernel read/write counters as read-only values.
- Most cache, readahead, perf, and perf-counter attributes are implemented by sending PARAM or PERF_COUNT service operations to the userspace daemon.
- Readahead sysfs operations are rejected when `ORANGEFS_FEATURE_READAHEAD` is not negotiated.
- Store paths validate numeric ranges before posting PARAM requests; two-value `readahead_count_size` is parsed specially.
- `orangefs_sysfs_init()` creates the root `orangefs` kobject plus `acache`, `capcache`, `ccache`, `ncache`, `perf_counters`, and `stats` children with default attribute groups.

## State, Dependencies, And Invariants

- `pc` and `stats` kobjects reject stores.
- Daemon-backed attributes require `is_daemon_in_service()` to succeed.
- Kobject error paths unwind with `kobject_put()` for already-created objects.
- Release callbacks free each allocated kobject and clear its global pointer.
