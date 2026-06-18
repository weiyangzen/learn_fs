<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf-success.c -->
# sources/test-tools/strace/tests/ioctl_perf-success.c

Purpose: injected-success test for successful `PERF_EVENT_IOC_ID` and `PERF_EVENT_IOC_QUERY_BPF` decoding. It focuses on read-style perf ioctls whose interesting output only appears when syscall injection makes the invalid-fd calls look successful.

Important APIs/types/functions: Uses `linux/perf_event.h`, `ioctl`, `PERF_EVENT_IOC_ID`, `PERF_EVENT_IOC_QUERY_BPF`, `uint64_t` id storage, a four-element `uint32_t` query buffer, `assert`, `sprintrc`, and injected return arguments `NUM_SKIP`/`INJECT_RETVAL`.

Control flow: exits quietly when run without injection arguments. Otherwise it parses skip count and expected nonnegative injected retval, loops on `PERF_EVENT_IOC_ID` until injection is observed, then asserts injected success for NULL, EFAULT, and populated `PERF_EVENT_IOC_ID` pointers. It repeats the pattern for `PERF_EVENT_IOC_QUERY_BPF`, covering NULL, EFAULT, truncated `{ids_len, ...}`, `{ids_len, prog_cnt, ids=ptr}`, and arrays with two or more program ids.

State and persistence behavior: no perf fd is valid; syscall injection simulates success and lets strace decode the local id/query buffers as output. No perf event state is created.

Dependencies/integration points: integrates perf UAPI xlat decoding with strace syscall injection.

Risks and test signals: requires exact injection configuration and stable query-buffer layout. Passing output confirms success-return formatting for perf id and BPF-query ioctls, including pointer fallback and bounded id-array printing.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_perf-success.c -->
