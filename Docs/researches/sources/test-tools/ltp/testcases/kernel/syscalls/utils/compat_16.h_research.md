<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.h

Purpose: Legacy 16-bit UID/GID syscall compatibility helpers for old LTP tests; it defines fallback syscall wrappers and range checks for old kernel ID widths.

Important APIs/types/functions: includes `errno.h`, `grp.h`, `sys/fsuid.h`, `sys/types.h`, `unistd.h`, `compat_gid.h`, `compat_uid.h`, `lapi/syscalls.h`; defines `setresuid`, `getresuid`, `setresgid`, `getresgid`, `SETGROUPS`, `GETGROUPS`, `SETUID`, `SETGID`, `SETFSUID`, `SETFSGID`, `SETREUID`, `SETREGID`; touches `syscall`, `write`, `raw syscall path`; uses constants/macros such as `TBROK`, `TCONF`, `TST_USE_COMPAT16_SYSCALL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is owned by tests that include these helpers. The headers/snippets normalize 16-bit UID/GID syscall compatibility at compile and runtime.

Dependencies and integration points: Depends on legacy/new LTP headers, `lapi/syscalls.h`, kernel old UID/GID typedefs, and build flags that select `TST_USE_COMPAT16_SYSCALL`. Direct includes: `errno.h`, `grp.h`, `sys/fsuid.h`, `sys/types.h`, `unistd.h`, `compat_gid.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_16.h -->
