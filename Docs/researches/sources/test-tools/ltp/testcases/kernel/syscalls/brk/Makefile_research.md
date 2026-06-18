# sources/test-tools/ltp/testcases/kernel/syscalls/brk/Makefile

Purpose: LTP leaf Makefile for `brk()` tests. It includes the standard testcase and generic leaf target makefiles without custom flags. Runtime libc-vs-syscall variants are in the C sources. State is build-only. Risks are minimal. Test signal is successful build of `brk01` and `brk02`.
