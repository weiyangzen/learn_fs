# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/Makefile

Purpose: builds the `fchmodat2` tests through the LTP testcase make framework.

Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`.

Control flow: sets the source root and includes common build fragments.

State/persistence behavior: no runtime state.

Dependencies/integration: covers newer `fchmodat2` tests and their LAPI syscall wrappers.

Risks/test signals: build-only risk, especially around availability of syscall numbers and LAPI headers.
