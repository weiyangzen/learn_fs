<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log.go -->
# sources/sync-backup/git-lfs/tasklog/log.go

Purpose: implements the task progress logger used to serialize task updates to an `io.Writer`, with TTY detection, optional forced progress, throttling, and task sequencing.

Important APIs/types/functions: `Logger`, `Option`, `ForceProgress`, `NewLogger`, `tty`, `Close`, `Waiter`, `Percentage`, `List`, `Simple`, `Enqueue`, `consume`, `logTask`, `logLine`, and `log`.

Control flow: `NewLogger` initializes sink, terminal width function, channels, wait group, applies options, detects TTY, and starts `consume`. `Enqueue` increments the wait group and sends tasks; a nil logger drains task updates in goroutines. `consume` forwards queued tasks to a processor goroutine sequentially. `logTask` reads updates, suppresses progress when stdout is not TTY and progress is not forced, applies throttling unless task is unthrottled, writes carriage-return progress lines, emits a final `, done.` line after the channel closes, calls optional `OnComplete`, and decrements the wait group.

State and persistence: in-memory goroutines/channels/waitgroup only; writes progress text to the sink. `Close` closes the enqueue channel and waits for outstanding tasks.

Dependencies and integration points: depends on `github.com/mattn/go-isatty`, `github.com/olekukonko/ts`, `Task`/`Update` types, and task constructors. Used by commands that need progress output.

Risks: `Enqueue` calls `wg.Add(len(ts))` even for nil tasks but skips sending nil, which can leave the wait group unbalanced if nil tasks are passed to a non-nil logger. Progress suppression checks `os.Stdout` TTY rather than only the configured sink, so behavior can differ in tests or redirected sinks unless `ForceProgress` is used.

Test signals: `log_test.go` covers sequential logging, progress suppression, nonblocking enqueue, throttling, durable/unthrottled updates, silent tasks, task constructor enqueue helpers, nil logger behavior, and nil close.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log.go -->
