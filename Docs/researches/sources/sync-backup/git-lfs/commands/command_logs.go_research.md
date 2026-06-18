<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_logs.go -->
# sources/sync-backup/git-lfs/commands/command_logs.go

Purpose: implements `git lfs logs` subcommands for listing, showing, clearing, and generating sample panic logs.

Important APIs/types/functions: `logsCommand`, `logsLastCommand`, `logsShowCommand`, `logsClearCommand`, `logsBoomtownCommand`, and `sortedLogs`; `cfg.LocalLogDir`, `os.ReadDir`, `os.ReadFile`, `os.RemoveAll`, and shared `Panic`.

Control flow: root lists filenames in the log directory; `last` selects the last filename from `sortedLogs`; `show` reads a named log file and writes it to stdout; `clear` removes the log directory; `boomtown` writes a sample trace and panics with a wrapped sample error.

State and persistence behavior: reads and deletes files in `.git/lfs/logs` or configured local log directory. `boomtown` creates a new log through normal panic logging.

Dependencies/integration points: integrates with `LoggedError`/`Panic` output from `commands.go` and tracerx logs.

Risks and test signals: risks include `sortedLogs` not actually sorting beyond filesystem order, path joining allowing only names relative to log dir but no explicit traversal defense, and clear deleting the whole log directory. Test signals include no logs, showing a named log, last log selection, clear behavior, and boomtown sample generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_logs.go -->
