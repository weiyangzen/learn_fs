# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/Makefile

Purpose: builds the `fchownat` syscall tests as an LTP leaf directory.

Important APIs/types/functions: `testcases.mk`, `../utils/compat_16.mk`, and `generic_leaf_target.mk`.

Control flow: includes common testcase rules, uid/gid compatibility rules, and generic leaf targets.

State/persistence behavior: no runtime state.

Dependencies/integration: supports tests that exercise both native and compatibility ownership syscalls.

Risks/test signals: build-only risk from make include availability.
