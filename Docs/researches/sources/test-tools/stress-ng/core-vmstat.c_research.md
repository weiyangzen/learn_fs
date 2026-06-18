# sources/test-tools/stress-ng/core-vmstat.c

## Purpose
`core-vmstat.c` implements periodic runtime reporting for VM, CPU, thermal, I/O, status, and RAPL power statistics while stress-ng runs.

## Important APIs, Types, And Functions
The public functions are `stress_find_mount_dev`, `stress_vmstat_start`, and `stress_vmstat_stop`. Internal structures `stress_vmstat_t` and `stress_iostat_t` hold sampled counters. Platform-specific `stress_read_vmstat` implementations read Linux `/proc/stat`, `/proc/meminfo`, and `/proc/vmstat`, BSD sysctls, OpenBSD `sysctl`, or macOS Mach APIs. Linux I/O helpers include `stress_iostat_iostat_name`, `stress_read_iostat`, and `stress_iostat_get`. `stress_vmstat_get` converts absolute counters to deltas. `stress_tz_info_get` reads thermal-zone temperatures for periodic thermal output.

## Control Flow
`stress_vmstat_start` reads configured delays for `iostat`, `raplstat`, `status`, `thermalstat`, `vmstat`, and `vmstat-units`. If all are disabled it returns. Otherwise it forks a child named `stat [periodic]`, initializes baseline samples, optionally resolves a block-device stat path, and loops until the global continue flag clears. The loop advances scheduled wake times, sleeps with nanosecond precision, refreshes counters whose interval expired, and prints headers every 25 samples. `stress_vmstat_stop` kills and waits for the child.

## State And Persistence
Process state includes static delays, `vmstat_units_kb`, previous VM/I/O samples, and `vmstat_pid`. The child reads kernel-provided counters and shared stress-ng state such as instance counts, start time, thermal-zone list, and RAPL domains. It writes only log/stdout output, not project files.

## Dependencies And Integration Points
It depends on core CPU frequency, RAPL, thermal-zone, killpid, time, load-average, filesystem path, and platform sysctl/Mach/proc helpers. Command-line options `--vmstat`, `--iostat`, `--thermalstat`, `--status`, `--raplstat`, and `--vmstat-units` feed it. Debian fast tests run stressors with `--vmstat 1`; kernel coverage uses vmstat/iostat/thermal/RAPL paths extensively.

## Risks
This file is highly platform-conditional. Linux proc parsing assumes field order and units; block-device detection mutates the device string while stripping partition suffixes and can fail for device-mapper or unusual mounts. Forked reporter cleanup must be reliable. Static previous counters are not thread-safe but run in a dedicated process. Unit scaling guards only zero scale, not odd user input semantics.

## Test Signals
Runtime output under `--vmstat 1`, `--iostat 1`, `--thermalstat 1`, `--status 5`, and `--raplstat 1` is the main signal. Cross-platform builds validate alternate `stress_read_vmstat` implementations. Kernel coverage's broad filesystem and CPU runs exercise mount-device resolution and periodic formatting.
