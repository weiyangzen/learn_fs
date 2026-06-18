# File Research: sources/os/linux/linux/mm/kasan/Makefile

Build rules for KASAN runtime and KUnit tests.

Key build controls:
- Disables KASAN, UBSAN, and KCOV instrumentation for KASAN runtime objects to avoid self-instrumentation recursion.
- Removes ftrace from runtime objects for the same reason.
- Adds KASAN runtime flags:
  - optional `-fno-conserve-stack`
  - `-fno-stack-protector`
  - `-DDISABLE_BRANCH_PROFILING`
- Configures test CFLAGS from `$(CFLAGS_KASAN)`, adding `-fno-builtin` when compiler memintrinsic instrumentation is not prefix-based.

Objects:
- Always builds `common.o` and `report.o`.
- Generic KASAN adds `init.o`, `generic.o`, `report_generic.o`, `shadow.o`, `quarantine.o`.
- Hardware tag KASAN adds `hw_tags.o`, `report_hw_tags.o`, `tags.o`, `report_tags.o`.
- Software tag KASAN adds `init.o`, `report_sw_tags.o`, `shadow.o`, `sw_tags.o`, `tags.o`, `report_tags.o`.
- KUnit test object includes C tests and Rust test helper when Rust is enabled.

Role:
This Makefile is part of KASAN correctness: instrumentation flags are as important as object selection because KASAN cannot safely instrument its own low-level runtime.
