<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xverbose.c -->
## sources/test-tools/strace/tests/arch_prctl-Xverbose.c

Purpose: Verbose xlat variant of the `arch_prctl` decoder test.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes `arch_prctl.c`.

Control flow: Uses common arch_prctl test logic with verbose xlat formatting.

State and persistence: No wrapper-local state.

Dependencies and integration: Builds a distinct test executable for `-X verbose` expectations.

Risks: Depends on shared macros in `arch_prctl.c` and xlat table names.

Test signals: Output should include raw values with symbolic comments for known and unknown arch/xfeature values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xverbose.c -->
