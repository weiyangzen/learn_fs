# File Research: sources/local-fs/ocfs2-tools/libtools-internal/progress.c

Implements terminal-aware progress display for ocfs2-tools.

Key responsibilities:
- Maintains a global list of active progress records, allowing nested progress displays.
- Renders either percentages for bounded work or spinner characters for unbounded work.
- Adapts output width using `COLUMNS`, shrinking long names to short names and then truncated names.
- Uses carriage return on terminals and newline on non-tty output.
- Provides clear/restore hooks so normal log output does not corrupt the progress line.

Important functions:
- `tools_progress_enable()` / `tools_progress_disable()` / `tools_progress_enabled()`.
- `tools_progress_start(long_name, short_name, count)`.
- `tools_progress_step(prog, step)`.
- `tools_progress_stop(prog)`.
- Internal rendering helpers: `progress_compute()`, `progress_printf()`, `truncate_printf()`.

Dependencies:
- Kernel-style list API.
- `isatty`, `gettimeofday`, environment variable `COLUMNS`.

Research notes:
- Updates are throttled to roughly 1/8 second and skipped if displayed percentage is unchanged.
- When disabled, callers get a static fake `disabled_prog`, so step/stop calls are harmless.
- Progress output is integrated with `verbose.c` via `tools_progress_clear()` and `tools_progress_restore()`.
