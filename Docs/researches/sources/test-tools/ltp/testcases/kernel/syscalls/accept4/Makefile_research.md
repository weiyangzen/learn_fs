# sources/test-tools/ltp/testcases/kernel/syscalls/accept4/Makefile

Purpose: LTP leaf Makefile for `accept4()` tests. It includes the standard testcase and generic leaf makefiles without custom flags. Runtime variants in `accept4_01.c` cover libc, direct syscall, and legacy `socketcall` where available. State is build-only. Risks are minimal unless platform syscall headers lack accept4/socketcall definitions handled by lapi. Test signal is successful compilation of the leaf target.
