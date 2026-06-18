<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_exe_runner.go -->
# sources/sync-backup/kopia/tests/testenv/cli_exe_runner.go

This file implements `CLIRunner` by launching an external Kopia executable. `CLIExeRunner` stores executable path, optional passthrough/debug fields, next stdin, extra file descriptors for socket activation, and log directory.

`Start` builds `exec.CommandContext` with `--log-dir`, merges environment variables, wires stdout/stderr pipes, optional stdin and `ExtraFiles`, starts the process, and returns readers plus wait/interrupt functions. Constructors resolve `KOPIA_EXE`, optionally use `kopia` under VS Code, unset `KOPIA_PASSWORD`, and create a temp log directory.

State is per-run process state and mutable `NextCommandStdin`/`ExtraFiles`. Dependencies are OS process APIs and test utilities. Risks include `ExtraFiles` persisting across starts unless caller clears it, process kill/signal errors ignored, and env leakage from `os.Environ`. Test signals include CLI integration and socket activation tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_exe_runner.go -->
