# sources/storage-engines/tikv/components/tikv_util/src/sys/cpu_time.rs

## Purpose
Provides cross-platform process CPU time and system CPU tick snapshots, with Linux-style CPU fields and a `ProcessStat` interval CPU-usage helper.

## Important APIs, Types, and Functions
- `LinuxStyleCpuTime` stores user/nice/system/idle/iowait/irq/softirq/steal/guest/guest_nice ticks and computes `total`.
- `LinuxStyleCpuTime::current` delegates to platform implementation.
- `cpu_time()` returns process CPU `Duration`.
- `ProcessStat::{cur_proc_stat,cpu_usage}` tracks previous wall and CPU times to compute usage ratio.
- Platform implementations cover Linux/FreeBSD `/proc/stat` plus `clock_gettime`, macOS host/getrusage APIs, and Windows process time APIs.

## Control Flow
On Linux/FreeBSD, `current` reads the first `/proc/stat` line and parses CPU tick fields. `cpu_time` uses `CLOCK_PROCESS_CPUTIME_ID`. `ProcessStat::cpu_usage` reads new process CPU duration, swaps old state, measures elapsed real time, and returns CPU delta divided by real-time delta.

## State and Persistence Behavior
Only `ProcessStat` instances hold in-memory previous readings. There is no global state beyond platform calls.

## Dependencies and Integration Points
Uses `libc`, `derive_more::{Add,Sub}`, and Windows/macOS system APIs under cfg. `quota_limiter` uses thread CPU time from a separate crate, while this module supports process-level monitoring.

## Risks
Platform support is uneven; Windows `current` is unsupported. Linux `/proc/stat` parsing expects all fields present. Long-running high-core Windows conversion comments note potential overflow risk when converting to nanoseconds. The CPU usage test is timing-sensitive.

## Test Signals
`test_process_usage` sleeps to expect near-zero usage, then spawns busy loops and expects usage above 0.9; it is marked in comments as a test that should run alone.
