<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xverbose.c -->
## sources/test-tools/strace/tests/arch_prctl-success-Xverbose.c

Purpose: Verbose xlat variant of the injected-success `arch_prctl` test.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes `arch_prctl-success.c`.

Control flow: Runs shared arch_prctl cases with injected successful returns and verbose xlat rendering.

State and persistence: No wrapper-local state.

Dependencies and integration: Provides coverage for successful pointer-output formatting in verbose mode.

Risks: Expected output is sensitive to xlat table content and injected return positioning.

Test signals: Output should show verbose xlat values and ` (INJECTED)` result annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xverbose.c -->
