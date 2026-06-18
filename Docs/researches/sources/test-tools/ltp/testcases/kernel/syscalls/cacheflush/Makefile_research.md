# sources/test-tools/ltp/testcases/kernel/syscalls/cacheflush/Makefile

Purpose: LTP leaf Makefile for architecture-specific `cacheflush()` tests. It includes standard testcase and generic leaf makefiles without extra flags. Runtime syscall availability is handled by conditional compilation in `cacheflush01.c`. State is build-only. Risks are architecture header availability. Test signal is either successful build of the test or compile-time `TCONF` path when the syscall is unsupported.
