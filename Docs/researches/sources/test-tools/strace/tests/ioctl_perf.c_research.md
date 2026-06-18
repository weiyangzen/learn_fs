<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf.c -->
# sources/test-tools/strace/tests/ioctl_perf.c

Purpose: tests baseline decoding of perf event ioctl commands on invalid descriptors, focusing on command names, scalar arguments, pointers, strings, and unknown command fallback.

Important APIs/types/functions: Uses raw `syscall(__NR_ioctl)`, `linux/perf_event.h`, `scno.h`, `PERF_EVENT_IOC_ENABLE`, `DISABLE`, `REFRESH`, `RESET`, `PERIOD`, `SET_OUTPUT`, `SET_FILTER`, `ID`, `SET_BPF`, `PAUSE_OUTPUT`, `QUERY_BPF`, and `MODIFY_ATTRIBUTES`.

Control flow: constructs representative scalar values, filter strings, pointers at page tails, and unknown commands. Each ioctl is issued on fd `-1` and the test prints the expected EBADF line with proper command and argument rendering.

State and persistence behavior: local buffers only; no perf event state is created.

Dependencies/integration points: depends on perf UAPI and strace xlat command tables. Integrates with syscall-number portability and string/pointer decoders.

Risks and test signals: command availability varies with headers. Passing output confirms perf ioctl name recognition, command-specific argument interpretation, and fallback for unknown perf ioctl numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf.c -->
