<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open.h

Purpose: Shared wrapper header for perf event tests; it exposes `perf_event_open()` through the raw syscall and centralizes perf-related constants used by sibling tests.

Important APIs/types/functions: includes `linux/types.h`, `linux/perf_event.h`, `inttypes.h`; defines `perf_event_open`; touches `perf_event_open`, `raw syscall path`; uses constants/macros such as `ENODEV`, `ENOENT`, `TBROK`, `TCONF`, `TERRNO`, `TINFO`.

Control flow: this file is consumed at compile time by sibling tests; any inline or fallback functions normalize missing libc/kernel interfaces before the test bodies run.

State and persistence behavior: Runtime state is perf event file descriptors, `perf_event_attr` settings, task/cpu binding, counter enable/disable state, and kernel perf permissions.

Dependencies and integration points: Depends on `perf_event_open.h`, kernel perf support, `/proc/sys/kernel/perf_event_paranoid`, root privileges, CPU affinity helpers, and perf ioctl/read ABI. Direct include dependencies include `linux/types.h`, `linux/perf_event.h`, `inttypes.h`.

Risks and test signals: fallback wrappers must match the real syscall ABI exactly; otherwise sibling tests can pass compile but exercise the wrong argument layout. Signals are compile success and correct behavior in the consuming tests.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/perf_event_open/perf_event_open.h -->
