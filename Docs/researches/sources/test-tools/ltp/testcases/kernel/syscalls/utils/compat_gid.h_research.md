<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_gid.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_gid.h

Purpose: Small compatibility header that selects `GID_T` and `GID_SIZE_CHECK()` for either old 16-bit GID syscall variants or native `gid_t`.

Important APIs/types/functions: includes `asm/posix_types.h`, `tst_common.h`; defines `GID_SIZE_CHECK`; touches `write`; uses constants/macros such as `TST_USE_COMPAT16_SYSCALL`.

Control flow: this file is consumed at compile time by sibling tests. Inline helpers or macros normalize feature detection and syscall dispatch before the consuming test callback runs.

State and persistence behavior: Runtime state is owned by tests that include these helpers. The headers/snippets normalize 16-bit UID/GID syscall compatibility at compile and runtime.

Dependencies and integration points: Depends on legacy/new LTP headers, `lapi/syscalls.h`, kernel old UID/GID typedefs, and build flags that select `TST_USE_COMPAT16_SYSCALL`. Direct includes: `asm/posix_types.h`, `tst_common.h`.

Risks and test signals: helper ABI mistakes affect every including testcase. Compile success plus correct behavior in the consuming tests are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/compat_gid.h -->
