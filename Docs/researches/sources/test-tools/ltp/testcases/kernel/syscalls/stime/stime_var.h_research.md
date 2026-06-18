<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime_var.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime_var.h

Purpose: Shared compatibility layer for stime tests; it reports whether libc `stime()` or the raw `__NR_stime` syscall is used and normalizes unsupported platforms into LTP configuration failures.

Important APIs/types/functions: includes `sys/time.h`, `config.h`, `tst_timer.h`, `lapi/syscalls.h`; defines `do_stime`, `stime_info`; touches `stime`, `syscall`, `time`, `raw syscall path`; uses constants/macros such as `TCONF`, `TINFO`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is the system wall clock. The tests deliberately change or attempt to change global system time and rely on privilege transitions plus libc/raw syscall dispatch.

Dependencies and integration points: Depends on `stime_var.h`, libc `stime()` when available, raw `__NR_stime` fallback, root privileges for success paths, and nobody-user credential switching for EPERM paths. Direct includes: `sys/time.h`, `config.h`, `tst_timer.h`, `lapi/syscalls.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime_var.h -->
