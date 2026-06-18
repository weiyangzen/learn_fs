<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun.go

This file implements the low-level external Kopia command runner. `Runner` stores executable path, temp config dir, fixed config-file args, and environment containing the test repository password.

`NewRunner` requires `KOPIA_EXE`, creates a temp config dir under the provided base dir, and returns a runner. `Run` logs command execution, builds args, runs the process with background context, captures stdout and stderr, and returns strings plus error. `RunAsync` starts a background command, captures stderr in a buffer, applies platform-specific parent-death behavior, and returns the command. `Cleanup` removes the config dir.

State is temp config and external process state. Dependencies are OS process APIs and `setpdeath`. Risks include no timeout/cancellation, verbose logs leaking command output, async stderr buffer unbounded until process exit, and required env var causing skip/failure. Tests cover construction and basic run behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun.go -->
