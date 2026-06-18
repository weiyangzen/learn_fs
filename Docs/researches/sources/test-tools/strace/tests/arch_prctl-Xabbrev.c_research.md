<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xabbrev.c -->
## sources/test-tools/strace/tests/arch_prctl-Xabbrev.c

Purpose: Compile-time xlat abbreviation variant of the `arch_prctl` decoder test.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `arch_prctl.c`.

Control flow: No local runtime logic; all behavior comes from `arch_prctl.c` with abbreviated xlat formatting enabled.

State and persistence: No state of its own.

Dependencies and integration: Built as a separate executable to compare `-X abbrev` decoding of arch_prctl commands and xfeature values.

Risks: Wrapper correctness depends on `arch_prctl.c` honoring `XLAT_ABBREV`.

Test signals: Expected output should show known constants in abbreviated symbolic form rather than raw or verbose forms.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-Xabbrev.c -->
