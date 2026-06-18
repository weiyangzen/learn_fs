# sources/storage-engines/tikv/components/tikv_util/src/metrics/process_linux.rs

## Purpose
Implements a Linux Prometheus process collector focused on CPU, virtual memory, RSS, and start time while deliberately omitting file descriptor collection to avoid fragmentation with many open descriptors.

## Important APIs, Types, and Functions
- `monitor_process()` registers `ProcessCollector`.
- `ProcessCollector::new()` creates descriptors and initializes immutable process start time from `procfs::boot_time_secs` and `/proc/self/stat`.
- `Collector::collect` reads current process stat, updates memory gauges, advances CPU counter, and returns metric families.
- `PAGESIZE` caches `libc::sysconf(_SC_PAGESIZE)`.

## Control Flow
On construction, metric descriptors are built and process start time is set if boot time and process stat are available. During each scrape, `/proc/self/stat` is read through `procfs`; errors produce an empty vector. CPU total is converted from ticks to seconds, compared to the existing counter value, and the counter is incremented by the delta.

## State and Persistence Behavior
Prometheus metric objects retain previous CPU counter value and start time. Memory gauges are overwritten each scrape. No durable persistence exists.

## Dependencies and Integration Points
Depends on `procfs`, `prometheus`, `libc`, and `crate::sys::thread::ticks_per_second`. It is selected only for Linux by `metrics/mod.rs`.

## Risks
The CPU counter update assumes monotonic process CPU time and that `total >= past`; abnormal resets could underflow. RSS uses page count times page size. `/proc` read failures silently suppress all process metrics for that scrape.

## Test Signals
No local tests; coverage is indirect through metrics registration and Linux process stat assumptions.
