# File Research: sources/os/bsd/netbsd-src/lib/libedit/tty.c

## Purpose
Implements libedit's tty/termios interface. It initializes terminal modes, switches between cooked/edit/quote modes, maps terminal special characters to editor commands, and implements an internal `stty` command.

## Main Components
- `ttyperm` defines set/clear masks for execute, edit, and quote modes across input, output, control, local, and character classes.
- `ttychar` defines default special control characters for each mode.
- `tty_map[]` maps terminal erase/kill/eof/word-erase/reprint/lnext controls to emacs, vi-insert, and vi-command bindings.
- `ttymodes[]` maps printable `stty` names to termios flags or control-character masks, guarded by platform feature macros.
- `tty_getty()` and `tty_setty()` wrap `tcgetattr()` / `tcsetattr()` and retry on `EINTR`.
- `tty_setup()` captures original terminal state, derives edit/execute modes, applies reset defaults, and binds special characters.
- `tty_init()` initializes mode templates and calls setup; `tty_end()` restores original tty settings.
- `tty_rawmode()`, `tty_cookedmode()`, `tty_quotemode()`, and `tty_noquotemode()` switch active terminal modes.
- `tty_bind_char()` rebinds editor maps when erase/kill/eof-style terminal characters change.
- `tty_stty()` prints or changes internal tty mode masks and control characters.
- `tty_get_signal_character()` returns displayable signal characters for selected signals when supported.

## Integration
Works with `terminal.c` for tab/meta/speed behavior, `keymacro` for binding changes, and libedit state in `EditLine`. It is central to enabling single-character interactive editing.

## Risks / Notes
- Heavy conditional compilation supports many termios variants.
- Correct behavior depends on preserving original tty state and restoring it on exit.
- `tty_rawmode()` deliberately tracks user changes made in cooked mode and propagates them into edit/execute modes.
