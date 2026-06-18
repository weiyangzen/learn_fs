# File Research: sources/local-fs/xfsdump/common/main.c

## Role

This is the shared `main()` implementation for xfsdump and xfsrestore, compiled under `DUMP` or `RESTORE`.

It coordinates process bootstrap, command-line preprocessing, logging, resource limits, inventory setup, drive/media/content initialization, signal handling, worker thread supervision, progress reporting, and interactive interrupt control.

## Startup Sequence

`main()` performs these steps:

- Verifies basic integer type sizes.
- Initializes locale/gettext.
- Initializes message logging in multiple phases.
- Records the parent pthread ID and registers `mlog_exit_flush()` with `atexit()`.
- Expands an option file if `GETOPT_OPTFILE` is present.
- Parses common options for help, progress reports, and stack limits.
- Initializes stream tracking.
- Adjusts process resource limits.
- Initializes the global lock and remote-tape warning behavior.
- Determines system page size.
- Captures the current working directory.
- Initializes the inventory base path.
- Handles help/version and inventory-print-only modes.
- For dump builds, requires effective UID root after inventory-print handling.
- Initializes dialog, child manager, drive manager, global headers, content, and media/drive streams.

## Execution Modes

Pipeline mode is detected when the first drive is an unnamed pipe. In pipeline mode, the program avoids the full multi-threaded signal/dialog supervisor and runs a single content stream directly.

Non-pipeline mode initializes all drives, creates one child thread per stream via `cldmgr_create()`, and enters a parent loop that joins child exits, processes signal flags, emits progress reports, and requests orderly stop/abort when needed.

## Signal Handling

`main.c` ignores `SIGPIPE` and treats write errors as normal I/O failures.

In non-pipeline mode it blocks and handles:

- `SIGINT`: optional status/control dialog; can request stop.
- `SIGHUP`: disables dialogs and requests stop.
- `SIGTERM`: disables dialogs and requests stop.
- `SIGQUIT`: requests abort/core behavior.
- `SIGALRM` and `SIGUSR1`: wakeups/progress handling.

`preemptchk()` is the cooperative preemption hook used by content code. It briefly releases pending signals at safe points, handles progress-only checks, and returns whether interruption was requested.

## Interactive Dialog

`sigint_dialog()` presents status/control choices through `dlog`:

- Interrupt the session.
- Change verbosity per subsystem or globally.
- Display I/O metrics.
- Restore-only inventory/remaining-object displays.
- Confirm media changes.
- Enable, disable, or change progress reports.
- Toggle log message levels, subsystems, and timestamps.

The dialog also prints content status lines and has timeout/default behavior.

## Option File Parsing

`loadoptfile()` scans for one option-file argument, opens and validates a regular file, concatenates executable name, option-file contents, and remaining command-line args into one buffer, tokenizes with quote/backslash awareness, strips quotes/escapes, and replaces `argc`/`argv`.

Supporting helpers are `strpbrkquotes()`, `stripquotes()`, and `shiftleftby1()`.

## Resource Limits

`set_rlimits()` normalizes resource limits:

- Ensures stack soft limit is within configured min/max bounds.
- Raises or lowers `RLIMIT_STACK` when possible.
- Sets file size and CPU soft limits toward hard/infinite limits.
- Restore builds also derive available virtual memory for tree/content budgeting.

## Shutdown And Exit Status

The parent loop requests stop through `cldmgr_stop()` and uses deadlines to escalate stuck shutdowns to abort/core. After all children exit, `content_complete()` determines whether the dump/restore completed, was interrupted, or remained incomplete. Final exit is recorded through `mlog_exit()` with richer RV hints where possible.

## Usage Output

`usage()` prints option summaries for dump or restore builds, with many options conditionally exposed under `REVEAL`.

## Important Globals

The file owns shared process state including:

- `progname`
- `homedir`
- `pipeline`
- `stdoutpiped`
- `parenttid`
- `sistr`
- `pgsz`
- `pgmask`
- progress-report timers
- signal-received flags
- stop/interruption state
