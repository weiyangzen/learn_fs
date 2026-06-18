<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.sh -->
## sources/test-tools/strace/tests/arch_prctl.sh

Purpose: Harness script for arch_prctl decoder tests that removes the intentionally emitted marker syscall from strace logs before diffing.

Important APIs/types/functions: Sources `init.sh`, uses `check_prog sed`, `run_prog`, `run_strace -earch_prctl`, `sed` range deletion, and `match_diff`.

Control flow: Verifies `sed`, runs the test program once to generate expected output, runs it under strace, strips log content through the marker `arch_prctl(0xffffffff..., 0xfffffffe)` failure line, then diffs filtered output against expectations.

State and persistence: Writes standard harness `$EXP`, `$LOG`, and `$OUT` files.

Dependencies and integration: Tied to `arch_prctl.c` marker call and expected formatting. Listed as a check script in `Makefile.am`.

Risks: The copyright year has an apparent typo (`20212`). More importantly, sed filtering depends on exact marker formatting across xlat modes.

Test signals: Passing diff after marker removal confirms tracer output matches program-generated expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl.sh -->
