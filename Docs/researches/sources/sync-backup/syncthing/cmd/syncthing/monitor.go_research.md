# sources/sync-backup/syncthing/cmd/syncthing/monitor.go

Purpose: outer monitor process for Syncthing, handling child restarts, log rotation/autoclose, panic log capture/reporting, and monitor self-restart after upgrades.

Important APIs/types/functions: stdout line buffers, restart/log/panic constants, `serveCmd.monitorMain`, `getBinary`, `copyStderr`, `copyStdout`, `restartMonitor`, platform restart helpers, `rotatedFile`, `newRotatedFile`, `Write`, `rotate`, `numberedFile`, `autoclosedFile`, `newAutoclosedFile`, `Write`, `Close`, `ensureOpenLocked`, `closerLoop`, `childEnv`, and `maybeReportPanics`.

Control flow: `monitorMain` configures stdout plus optional file logging with rotation and autoclosed files, resolves the executable, filters child env and adds `STMONITORED=yes`, reports existing panics, enforces restart-loop protection, starts the inner process, copies stdout/stderr concurrently, forwards INT/TERM/SIGHUP as stop/restart signals, interprets child exit codes, self-execs on upgrade on Unix, and restarts on crashes unless disabled. `copyStderr` detects panic/fatal/runtime prefixes, creates timestamped panic logs, includes early and recent stdout context, and triggers crash reporting after close.

State and persistence: writes log files with rotation, panic logs, and reported panic renames through `crash_reporting.go`. Keeps first 10 and last 50 stdout lines in memory for panic context.

Dependencies/integration: tightly coupled with `serveCmd.Run`, `svcutil` exit codes, locations, build OS checks, crash reporting config, and platform-specific restart behavior.

Risks and test signals: restart-loop threshold protects against rapid crash cycles. Log rotation errors are printed to stdout rather than fatal. Autoclosed files reduce long-held descriptors. Existing monitor tests are outside this work item, but not mapped here; this file's assigned scope has no direct mapped test doc.
