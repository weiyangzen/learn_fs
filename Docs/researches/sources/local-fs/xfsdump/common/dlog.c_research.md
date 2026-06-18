# File Research: sources/local-fs/xfsdump/common/dlog.c

Purpose: implements the operator-dialog abstraction used for interactive dump/restore prompts.

Key behavior:
- `dlog_init` initializes dialog state, parses options, and may disable dialogs for force mode.
- In restore mode, if input comes from stdin (`-`), it opens `/dev/tty` for dialogs.
- `dlog_allowed`, `dlog_desist`, and `dlog_fd` expose dialog state.
- `dlog_begin` locks `mlog` and prints preamble strings; `dlog_end` prints postamble strings and unlocks.
- `dlog_multi_query` displays numbered choices, highlights/defaults/timeouts, reads a response, validates it, and returns a zero-based choice index or exception index.
- `dlog_string_query` lets the caller print custom context through a callback and then reads an arbitrary string.
- `dlog_sighandler` consumes only registered dialog signals and records the first signal seen.
- `promptinput` handles prompt display, timeout calculation, temporary signal unblocking, `select` polling, partial line reads, timeout, and signal-to-exception mapping.

Interactions:
- Uses `mlog`/`mlog_va` for all output and coordinates with the logging lock.
- Integrates with process signal handling by registering SIGINT, SIGHUP/SIGTERM, and SIGQUIT only while waiting for input.
- Uses command-line options from `getopt.h`, including force and no-timeouts behavior.

Risks/notes:
- Dialog input is tied to a single static fd and static signal state.
- `promptinput` polls every 100 ms so it can notice signals even when another thread handles them.
- The code assumes callers only call query functions when `dlog_allowed_flag` is true; assertions enforce this.
