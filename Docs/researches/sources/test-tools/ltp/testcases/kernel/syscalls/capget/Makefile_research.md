# sources/test-tools/ltp/testcases/kernel/syscalls/capget/Makefile

Purpose: LTP leaf Makefile for `capget()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime capability drops and syscall variants are declared in the C files. State is build-only. Risks are minimal and limited to capability header/syscall availability. Test signal is successful build of `capget01` and `capget02`.
