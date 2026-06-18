# sources/test-tools/ltp/testcases/kernel/syscalls/adjtimex/Makefile

Purpose: LTP leaf Makefile for `adjtimex()` tests. It includes the standard testcase and generic leaf target makefiles without extra linker flags. Runtime root, syscall variant, and time-state restoration logic are in the C files. State is build-only. Risk is low because all special behavior is source-level. Test signal is successful compilation of the three adjtimex test binaries.
