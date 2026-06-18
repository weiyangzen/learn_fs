# sources/test-tools/stress-ng/stress-cpu-online.c

## Purpose
This Linux-only stressor repeatedly takes CPUs offline and online through sysfs to exercise CPU hotplug, scheduler affinity, and kernel CPU-online state transitions. It requires root privileges and advertises options for trying CPU affinity during hotplug and for including CPU 0.

## Important APIs, Types, And Functions
The exported object is `stress_cpu_online_info`, classified as CPU, OS, and pathological work. `stress_cpu_online_supported()` checks root and writable `/sys/devices/system/cpu/cpu1/online`. `stress_cpu_online_set()` writes `"0\n"` or `"1\n"` to a CPU online file and classifies transient errors as no-resource. `stress_cpu_online_get()` reads online state. `stress_cpu_online_set_affinity()` optionally pins the caller to a target CPU. `stress_cpu_online()` contains CPU discovery, child affinity helper setup, hotplug loop, cleanup, and metrics.

## Control Flow
The stressor reads `cpu-online-affinity` and `cpu-online-all`, verifies root, bounds configured CPUs to 65536, and builds a boolean map of CPUs with readable/writable `online` control files. A helper child may be forked; the parent writes upcoming CPU ids through a pipe and the child repeatedly tries to set its affinity to CPUs being offlined. The parent then selects CPUs sequentially, reverse sequentially, or randomly depending on instance number, skips CPU 0 unless requested, checks current online state, optionally pins itself, writes offline, verifies state, writes online, verifies state, updates timing counters, and yields.

## State And Persistence
The only durable external state is sysfs CPU online status, and the stressor explicitly restores all controllable CPUs online before exit. In-process state includes the CPU capability map, child pid/pipe, previous CPU selection, and timing counters. Metrics report milliseconds per offline and online action.

## Dependencies And Integration Points
This file depends on Linux sysfs CPU hotplug files, scheduler affinity APIs, stress-ng process state/sync/metrics helpers, root privileges, and `core-killpid` cleanup. It integrates with option parsing through `OPT_cpu_online_affinity` and `OPT_cpu_online_all`.

## Risks
CPU hotplug is disruptive and can destabilize workloads, trigger kernel/driver bugs, or interact badly with cpuset and affinity policy. Running multiple instances disables `--cpu-online-all` to reduce CPU 0 risk, but other CPUs can still be critical to the host. Failures such as `EBUSY` and `EOPNOTSUPP` are expected on some systems. Cleanup must run to restore all CPUs online and kill the helper child.

## Test Signals
Signals include skip behavior for non-root or unwritable sysfs, correct restoration of online state after interruption, timing metrics, absence of leaked helper processes, and successful operation with and without affinity mode. Kernel logs, scheduler warnings, and CPU hotplug tracepoints are important external validation.
