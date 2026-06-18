# sources/test-tools/ltp/testcases/kernel/syscalls/capset/Makefile

Purpose: LTP leaf Makefile for `capset()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime root, fork, and capability setup are in C files. State is build-only. Risks are minimal. Test signal is successful compilation of all capset tests.
