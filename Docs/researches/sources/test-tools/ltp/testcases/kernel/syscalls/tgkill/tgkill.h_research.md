<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill.h

Purpose: Shared raw-syscall wrapper for `tgkill()` tests, centralizing thread-group signal delivery through `tst_syscall(__NR_tgkill, ...)`.

Important APIs/types/functions: includes `config.h`, `lapi/syscalls.h`; defines `sys_tgkill`, `sys_gettid`; touches `raw syscall path`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct includes: `config.h`, `lapi/syscalls.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill.h -->
