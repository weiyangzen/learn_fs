# sources/test-tools/stress-ng/stress-klog.c

Purpose: implements `klog`, a Linux kernel syslog interface stressor that reads kernel log buffers and exercises valid and invalid `klogctl` actions.

Important APIs/types/functions: action constants mirror Linux syslog commands. `stress_klog_supported()` probes `SYSLOG_ACTION_SIZE_BUFFER`. `stress_klog()` uses `shim_klogctl()` for buffer-size, read, open/close, unread-size, clear, console toggles, console level, and invalid command tests.

Control flow: support probing requires access to the kernel log. The worker determines buffer size, skips zero-sized logs, caps allocation at 4 MiB, sync-starts, then loops with a random read length. Each iteration tests invalid sizes and buffers, performs `READ_ALL`, validates it does not return more than requested, runs no-op open/close and size queries, optionally forces privileged actions to fail when lacking syslog/admin capability, tests invalid console levels and command type, and increments bogo ops.

State and persistence behavior: only a heap buffer is retained. Privileged clear/read-clear and console actions are only attempted when not capable, so normal runs avoid mutating kernel log state except for reads and no-op commands.

Dependencies and integration points: requires the `syslog` syscall or stress-ng klog shim and capability checks. Registered as `CLASS_OS`, always verified, with a support probe.

Risks: access to klog is commonly restricted by `dmesg_restrict`, capabilities, containers, or lockdown. Kernel logs can be large or concurrently changing, so return sizes are inherently racy.

Test signals: verify skip messaging without `CAP_SYSLOG`/`CAP_SYS_ADMIN`, successful bounded allocation, no over-read result, and accepted behavior across restricted and privileged systems.
