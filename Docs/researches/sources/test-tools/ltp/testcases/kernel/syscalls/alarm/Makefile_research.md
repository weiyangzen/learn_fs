# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/Makefile

Purpose: LTP leaf Makefile for `alarm()` behavior tests. It includes standard testcase and generic leaf makefiles without custom flags. Runtime timing, signal handlers, fork behavior, and timeout metadata are contained in the C files. State is build-only. Risks are minimal. Test signal is successful build of the alarm test binaries.
