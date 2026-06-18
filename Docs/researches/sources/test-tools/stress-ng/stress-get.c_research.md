<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-get.c -->
# sources/test-tools/stress-ng/stress-get.c Research

Purpose: implements `get`, an OS stressor that cycles through many `get*` and related information syscalls/libc calls, including identity, process group, resource limit, time, filesystem, namespace, and system information APIs.

Important APIs/types/functions: `stress_get_func_t` is the method signature. `stress_get_funcs[]` contains the dispatch list. Helpers cover `getcwd`, ids/groups, `getpriority`, `getresuid/gid`, `getrlimit`, `ugetrlimit`, `prlimit`, `_sysctl`, `getrusage`, `getsid`, `gettid`, `getcpu`, `time`, `gettimeofday`, `uname`, `sysfs`, `statfs`, `statvfs`, `adjtimex`, `adjtime`, namespace listing, and more. `stress_segv_handler()` uses `siglongjmp` to recover from intentional fault probing.

Control flow: `stress_get()` reads `get-slow-sync`, checks time-setting capability, installs SIGSEGV recovery, caches mount paths, records PID and verify mode, synchronizes, then repeatedly selects a function either sequentially or from a time-derived synchronized index. Each selected helper performs valid and often intentionally invalid variants, reporting failures only for unexpected errors under verify rules. After the loop, it calls `getlogin()` once because that may reset alarms, deinitializes, and frees mount strings.

State and persistence: static indices inside helpers rotate through rlimit, priority, rusage, filesystem, and mount arrays. Mount strings are allocated by `stress_mount_get()` and freed at exit. `mypid`, `verify`, capability flags, and mount arrays are process-global. No durable state is written.

Dependencies and integration: depends on many platform headers and stress-ng shims for capabilities, mounts, time/syscalls, bad/racy PID generation, mapped guard pages, sync/state/logging, and options. It registers as unimplemented without `siglongjmp`.

Risks: behavior varies heavily by OS, libc, capabilities, namespace support, VDSO behavior, and deprecated syscall availability. Several helpers intentionally ignore errors to increase syscall coverage. Intentional invalid pointer/protected-page probes require reliable signal recovery.

Test signals: bogo progress indicates call cycling. Verify failures identify unexpected syscall errors or mismatched time/sysfs/getcwd/uname behavior. Test slow-sync with multiple workers, limited capabilities, container namespaces, and alternate libc/kernel combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-get.c -->
