# sources/test-tools/ltp/testcases/kernel/syscalls/link/Makefile

Purpose: builds the `link` syscall tests with standard LTP infrastructure. It includes `testcases.mk` and `generic_leaf_target.mk` without extra libraries. There is no runtime state in the Makefile. Integration points are the old and new LTP harnesses used by the C files and filesystem test setup such as read-only mount handling. Risks are minimal beyond build-system path correctness. Test signal is successful compilation of `link02`, `link04`, `link05`, `link08`, and any adjacent link tests in the directory.
