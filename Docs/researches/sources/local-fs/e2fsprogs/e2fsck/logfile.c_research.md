# File Research: sources/local-fs/e2fsprogs/e2fsck/logfile.c

## Purpose
Sets up e2fsck output and problem log files, including filename expansion and delayed writing when log directories are not yet writable.

## Filename Expansion
`expand_logfn()` expands `%` expressions including:
- date/time fields,
- hostname,
- device basename,
- PID,
- epoch seconds,
- username,
- UTC switch `%U`,
- literal `%`.

## Log Opening
`set_up_log_file()`:
- Reads profile options for log filename, log directory, fallback directory, and wait behavior.
- Expands dynamic filename.
- Tries direct path, configured log directory, fallback directory.
- If enabled and directories are unavailable, uses `save_output()`.

## Delayed Output
`save_output()`:
- Creates a pipe and forks.
- Child daemonizes, buffers all parent output in memory, then repeatedly tries target paths until one opens, writes buffered output, and exits.
- Parent receives a `FILE *` to the pipe.

## Integration
`set_up_logging()` populates `ctx->logf` and `ctx->problem_logf`. The behavior is documented in `e2fsck.conf.5.in`.

## Risks / Notes
Delayed logging can buffer unbounded output in memory until a log path becomes writable.
