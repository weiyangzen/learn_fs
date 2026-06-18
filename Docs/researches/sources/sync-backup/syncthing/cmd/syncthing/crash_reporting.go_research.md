# sources/sync-backup/syncthing/cmd/syncthing/crash_reporting.go

Purpose: uploads panic logs to the configured crash-reporting server and sanitizes log content before upload.

Important APIs/functions: `uploadPanicLogs`, `uploadPanicLog`, and `filterLogLines`; constants `headRequestTimeout` and `putRequestTimeout`.

Control flow: `uploadPanicLogs` globs `panic-*.log`, sorts newest-first, skips already reported files, uploads each, and renames successful uploads to `.reported.log`. `uploadPanicLog` reads a file, filters log lines for privacy, hashes the filtered content as the panic ID, checks if the crash is already known with HEAD, and uploads with PUT on miss. `filterLogLines` keeps the first line and the panic trace starting at a `Panic ` line while stripping device ID prefixes.

State and persistence: reads panic logs and renames reported ones. Network state is remote crash server objects keyed by SHA-256 of filtered content.

Dependencies/integration: called by monitor crash-reporting flow when config enables crash reporting.

Risks and test signals: filtering is privacy-sensitive and pattern-based; stack traces not beginning with `Panic ` may retain only the first line. HTTP responses must be closed and non-200 PUT returns errors. Unit test covers device-prefix stripping and log-line removal.
