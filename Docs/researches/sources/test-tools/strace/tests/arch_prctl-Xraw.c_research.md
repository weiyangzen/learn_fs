<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xraw.c -->
## sources/test-tools/strace/tests/arch_prctl-Xraw.c

Purpose: Raw numeric xlat variant of the `arch_prctl` decoder test.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes `arch_prctl.c`.

Control flow: Compiles the common arch_prctl test so expected output uses raw numeric values for xlat-controlled fields.

State and persistence: No wrapper-local state.

Dependencies and integration: Part of the xlat mode matrix in `Makefile.am`.

Risks: A change in `arch_prctl.c` output macros can desynchronize this variant.

Test signals: Output should prefer numeric command/xfeature values where xlat mode applies.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xraw.c -->
