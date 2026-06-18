# sources/storage-engines/tikv/components/tikv_util/src/sys/mod.rs

## Purpose
Centralizes system utility exports and platform quota helpers: CPU/memory quotas, global memory usage/high-water checks, cache info, mount-point comparison, hostname, and submodules for disk/thread/IO inspection.

## Important APIs, Types, and Functions
- Public modules: `cpu_time`, `disk`, `inspector`, `ioload`, `thread`, and Linux-only `cgroup`.
- Re-exports selected `sysinfo` traits and defines `HIGH_PRI`.
- `SysQuota::{cpu_cores_quota,cpu_cores_quota_current,memory_limit_in_bytes,memory_limit_in_bytes_current,log_quota}` combines hardware, cgroup, and env-var limits.
- Global memory functions: `record_global_memory_usage`, `get_global_memory_usage`, `register_memory_usage_high_water`, `memory_usage_reaches_high_water`, and `memory_usage_reaches_near_high_water`.
- `cache_size`, `cache_line_size`, `path_in_diff_mount_point`, and `hostname`.

## Control Flow
Linux quota methods use a lazy `SELF_CGROUP` snapshot for stable quota and construct a fresh `CGroupSys` for current quota. CPU quota starts from `num_cpus`, then takes the minimum with cpuset and cgroup CPU quota, then applies `TIKV_CPU_CORES_QUOTA` if valid. Memory quota takes the minimum of sysinfo total memory and cgroup memory limit. Memory high-water checks compare the recorded RSS against either exact high water or a near-high-water margin: 90% below 10 GiB usage and fixed 1 GiB margin above.

## State and Persistence Behavior
Global memory usage and high-water mark are static atomics. The Linux cgroup snapshot is lazy static and can become stale if cgroup limits change; current variants re-read. No state is durable.

## Dependencies and Integration Points
Depends on `sysinfo`, `num_cpus`, `procinfo`, `page_size`, `fail`, `ReadableSize`, Linux cgroup helpers, and platform hostname APIs. Other modules and resource managers use these helpers for quota sizing and pressure checks.

## Risks
`record_global_memory_usage` unwraps `procinfo::pid::statm_self` on Linux. Environment quota parsing silently ignores invalid values. Mount-point detection parses `/proc/mounts` manually and returns false on errors, favoring non-disruptive behavior over strict detection.

## Test Signals
Tests cover hostname parity with the `hostname` command, mount-point difference behavior, mount parsing with spaces/tabs/comments, disk-space stats, and near-high-water threshold decisions.
