# sources/test-tools/ltp/testcases/kernel/syscalls/clock_adjtime/Makefile

Purpose: LTP leaf Makefile for `clock_adjtime()` tests. It includes standard testcase rules, links `-lrt`, and delegates to generic leaf targets. Runtime syscall/time64 variants and wall-clock restoration are in C files. State is build-only. Dependencies are realtime library and LTP syscall/timex helpers. Risks are older platforms without syscall variants handled by conditional arrays. Test signal is successful compilation of the clock adjustment tests.
