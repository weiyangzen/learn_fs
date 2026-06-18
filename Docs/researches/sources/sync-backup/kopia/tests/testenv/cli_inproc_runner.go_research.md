<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_inproc_runner.go -->
# sources/sync-backup/kopia/tests/testenv/cli_inproc_runner.go

This file implements `CLIRunner` by invoking Kopia CLI subcommands in-process. `CLIInProcRunner` stores guarded next stdin and an optional `CustomizeApp` hook.

`Start` creates a new CLI app, enables dangerous commands, assigns a unique env prefix, applies customization, transfers one-shot stdin under a mutex, writes prefixed env vars, and calls `RunSubcommand`. `SetNextStdin` sets the next stdin. `NewInProcRunner` skips when external integration tests are preferred and registers an in-memory storage provider.

State is mostly per-command app state plus process environment variables with unique prefixes. Dependencies include kingpin and Kopia CLI internals. Risks include process-global env accumulation, in-process command side effects leaking between tests, and limited fidelity versus real process execution. Tests use it for faster CLI coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_inproc_runner.go -->
