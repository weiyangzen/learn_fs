<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun_test.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun_test.go

This file tests the Kopia runner wrapper. It manipulates `KOPIA_EXE`, verifies missing-executable errors, creates runners with temp config, and runs commands expected to succeed or fail.

The tests validate environment gating, temp config setup, fixed arg injection, and error propagation from subprocess execution. They depend on a real Kopia executable when available and skip/branch otherwise.

Risks covered include missing env configuration and basic process failure. Residual risks include async server processes, output parsing, and timeout behavior. Higher-level snapshotter tests cover more command semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun_test.go -->
