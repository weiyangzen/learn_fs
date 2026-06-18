# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/Makefile

Purpose: builds the `fchmod` syscall tests as a standard LTP leaf directory.

Important APIs/types/functions: `top_srcdir`, `testcases.mk`, and `generic_leaf_target.mk`.

Control flow: declares the default top source location and includes LTP common testcase and generic leaf build rules.

State/persistence behavior: no runtime state; build outputs are managed by the included make fragments.

Dependencies/integration: integrates all local `fchmod*.c` files and `fchmod.h` with the LTP build framework.

Risks/test signals: low logic risk. Failures are build-system or environment failures.
