# sources/test-tools/ltp/testcases/kernel/syscalls/arch_prctl/Makefile

Purpose: LTP leaf Makefile for x86 `arch_prctl()` tests. It includes standard testcase and generic leaf makefiles without extra flags. Runtime architecture gating is declared in `arch_prctl01.c`. State is build-only. Risks are minimal. Test signal is successful compilation where syscall headers are available.
