## sources/test-tools/stress-ng/stress-vdso.c

Purpose: Implements `vdso`, discovering callable vDSO symbols and measuring their invocation cost.

Important APIs/types/functions: `stress_vdso_info`, wrapper functions for getcpu/gettimeofday/time/clock_gettime/clock_getres, `dl_wrapback`, symbol-list helpers, `stress_vdso_supported`, and `stress_vdso`; option `vdso-func` restricts to one symbol.

Control flow: support gets `AT_SYSINFO_EHDR`, iterates program headers, parses the vDSO dynamic section hash/string/symbol tables, and records known function symbols. Runtime removes duplicate aliases, optionally filters by configured symbol, calls each wrapper until stop, then runs dummy wrappers to estimate overhead and subtract it from per-call timing.

State and persistence: global linked list `vdso_sym_list` is allocated during support probing and freed at the end of the stressor; no external state.

Dependencies/integration: ELF/linker structures, `getauxval`, `dl_iterate_phdr`, stress-ng setting and metric APIs.

Risks: fragile across architectures/libcs with different symbol names or missing SysV hash; global symbol list means support/runtime ordering matters.

Test signals: reports nanoseconds per call excluding overhead plus overhead nanoseconds; invalid `vdso-func` fails with allowed names.
