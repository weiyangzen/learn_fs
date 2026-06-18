# File Research: sources/os/bsd/netbsd-src/lib/libedit/terminal.h

## Purpose
Internal libedit header for terminal state, capability flags, function-key metadata, and terminal API prototypes.

## Main Content
- Defines `funckey_t` for symbolic function keys: name, termcap index, bound function, and macro type.
- Defines `el_terminal_t`, which stores terminal name, size, flags, termcap buffers, string/numeric capability arrays, and function-key array.
- Defines terminal capability flags such as `TERM_CAN_INSERT`, `TERM_CAN_DELETE`, `TERM_CAN_CEOL`, `TERM_CAN_TAB`, `TERM_HAS_META`, and margin behavior flags.
- Defines function-key indexes for down/up/left/right/home/end/delete.
- Declares all terminal operations implemented by `terminal.c`.

## Integration
Used inside libedit's `EditLine` state via `el_terminal_t`; the `EL_CAN_*` and `EL_HAS_*` macros are used by rendering, tty mode setup, and cursor movement.

## Risks / Notes
The header is tightly coupled to `terminal.c`'s termcap indexes and libedit's internal `coord_t`, `keymacro_value_t`, and `EditLine` types.
