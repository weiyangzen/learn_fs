# sources/test-tools/ltp/testcases/kernel/syscalls/acct/Makefile

Purpose: LTP leaf Makefile for process accounting syscall tests. It includes standard testcase and leaf target makefiles without extra flags. Runtime kconfig, root, read-only filesystem, helper executable, and accounting file behavior are declared in the C files. State is build-only. Risks are minimal, though `acct02` depends on building `acct02_helper` alongside the test binary. Test signal is successful compilation of `acct01`, `acct02`, and helper.
