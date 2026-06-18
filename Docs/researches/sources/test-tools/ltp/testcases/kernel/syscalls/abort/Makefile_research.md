# sources/test-tools/ltp/testcases/kernel/syscalls/abort/Makefile

Purpose: LTP leaf Makefile for abort syscall/libc behavior tests. It includes standard `testcases.mk` and `generic_leaf_target.mk` without custom flags or libraries. Runtime needs such as tmpdir, fork, and core limit setup are declared in `abort01.c`. State is build-only. Risks are minimal and limited to make include path correctness. Test signal is successful build of `abort01`.
