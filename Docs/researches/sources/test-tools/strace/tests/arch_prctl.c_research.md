<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.c -->
## sources/test-tools/strace/tests/arch_prctl.c

Purpose: Comprehensive decoder test for x86 `arch_prctl` commands, unknown ranges, pointer-output commands, CPUID toggles, and xfeature permission/query commands.

Important APIs/types/functions: Defines `sys_arch_prctl`, `arch_prctl_marker`, `ARRAY_END`, `INJ_STR`, uses `struct strval32/64`, `TAIL_ALLOC_OBJECT_CONST_PTR`, xlat tables `archvals`, `x86_xfeature_bits`, `x86_xfeatures`, and `XLAT_*` macros.

Control flow: Emits a marker call for filtering/injection, optionally locks onto injected return values, allocates output buffers, iterates unknown command ranges with zero/dummy/pointer args, iterates known default commands, tests `ARCH_GET_GS`/`ARCH_GET_FS` pointer output after setting related values, tests `ARCH_GET_CPUID`, iterates xfeature mask getters with many masks, and tests xfeature permission request commands where positive return masks are decoded.

State and persistence: Temporary buffers hold returned segment/xfeature values. Some calls attempt to set FS/GS/CPUID/xfeature state, but failures are acceptable and process-local.

Dependencies and integration: Shared by raw/abbrev/verbose and injected-success wrappers; `arch_prctl.sh` filters marker output from strace logs. Requires `__NR_arch_prctl` and x86-specific constants.

Risks: Real arch_prctl effects are architecture- and kernel-dependent. Injected mode changes output paths. Xfeature tables must stay synchronized with kernel definitions.

Test signals: Expected output covers unknown commands, known command names, pointer success/failure formatting, xfeature mask flag expansion, request return masks, xlat mode differences, and clean exit or skip.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.c -->
