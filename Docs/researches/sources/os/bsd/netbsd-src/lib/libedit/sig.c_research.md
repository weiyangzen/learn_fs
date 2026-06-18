# File Research: sources/os/bsd/netbsd-src/lib/libedit/sig.c

## Purpose
Manages libedit's temporary signal handling while reading/editing a line.

## Main Interfaces
- `sig_init`: allocate signal state and initialize signal mask/actions.
- `sig_end`: free signal state.
- `sig_set`: install libedit's handler for configured signals.
- `sig_clr`: restore saved handlers.
- `sig_handler`: common handler for all tracked signals.

## Signal Policy
Tracked signals are `SIGINT`, `SIGTSTP`, `SIGQUIT`, `SIGHUP`, `SIGTERM`, `SIGCONT`, and `SIGWINCH`. The handler records the signal number in `el_signal->sig_no`, restores terminal state as needed, restores the previous handler for that signal, unblocks, and re-raises the signal so the caller/application sees normal signal behavior.

`SIGCONT` restores raw mode and refreshes display. `SIGWINCH` resizes the editor. Other signals switch the terminal back to cooked mode.

## Dependencies
Uses terminal raw/cooked helpers, refresh/redisplay functions, `el_resize`, and `common.h`.

## Risks And Notes
- A static global `sel` points to the active `EditLine`, so this machinery is not safe for concurrent independent editors.
- The handler calls several routines that are not generally async-signal-safe; this is legacy terminal-editor behavior rather than strict POSIX signal-minimal design.
