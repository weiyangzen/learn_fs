# sources/test-tools/ltp/testcases/kernel/syscalls/linkat/Makefile

Purpose: builds `linkat` tests and suppresses format-string warnings with `CPPFLAGS += -Wno-error` because the legacy test sources have messy diagnostics. It includes LTP testcase and generic leaf rules. There is no runtime state. Integration points are old `test.h`, raw `__NR_linkat`, and safe macros in the C files. Risks are warning suppression hiding non-format issues only if warnings are globally promoted. Test signal is successful build despite legacy format strings.
