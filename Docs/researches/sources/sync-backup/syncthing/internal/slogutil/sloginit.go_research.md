# sources/sync-backup/syncthing/internal/slogutil/sloginit.go

Purpose: Initializes Syncthing's global slog handler, default recorders, default line format, and package-level tracker.

Important APIs/types/functions: Defines `GlobalRecorder`, `ErrorRecorder`, `DefaultLineFormat`, `globalLevels`, `globalFormatter`, and `slogDef`. `logWriter` returns `io.Discard` when `LOGGER_DISCARD` is set, otherwise stdout. `init` installs `slogDef` as the process default logger.

Control flow: Package initialization constructs the formatter with both recorders and an output writer, then calls `slog.SetDefault`.

State and persistence behavior: Creates global in-memory recorder state. Output goes to stdout unless explicitly discarded through environment configuration.

Dependencies and integration points: This is the root logging setup used throughout Syncthing, including API log endpoints and legacy adapters.

Risks: Package import order controls when the default logger is installed. `LOGGER_DISCARD` disables stdout output but still records in memory. Global mutable formatter/level state can affect tests if not isolated.

Test signals: Formatter and API tests depend on this initialization behavior, though they often use custom recorders.
