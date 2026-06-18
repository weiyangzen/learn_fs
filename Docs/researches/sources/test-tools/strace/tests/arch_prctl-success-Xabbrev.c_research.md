<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xabbrev.c -->
## sources/test-tools/strace/tests/arch_prctl-success-Xabbrev.c

Purpose: Abbreviated xlat variant of the injected-success `arch_prctl` test.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `arch_prctl-success.c`, which defines `INJECT_RETVAL` before including `arch_prctl.c`.

Control flow: Runtime is inherited from `arch_prctl.c` with injected return handling and abbreviated xlat output.

State and persistence: No state beyond the included test's temporary buffers and real arch_prctl effects.

Dependencies and integration: Exercises successful-return decoder paths that may be hard to trigger on the host kernel.

Risks: Requires the harness invocation to pass injection skip/retval arguments expected by the included code path.

Test signals: Expected lines include ` (INJECTED)` and abbreviated symbolic constants.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xabbrev.c -->
