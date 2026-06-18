# File Research: sources/os/bsd/netbsd-src/lib/libedit/chared.h

This internal header declares libedit character editor state and helper APIs.

Key types:
- `c_undo_t`: saved line length, cursor, and buffer for vi undo.
- `c_redo_t`: redo insertion buffer, command, invoking character, count, and action.
- `c_vcmd_t`: active vi operator action and position.
- `c_kill_t`: kill/yank buffer, end pointer, and mark.
- `el_chared_t`: aggregates undo, kill, redo, vi command state, resize callback, and alias callback.

Important constants:
- `VI_MOVE` enables vi-like cursor movement on insert/command transitions.
- Action flags: `NOP`, `DELETE`, `INSERT`, `YANK`.
- Direction constants: `CHAR_FWD`, `CHAR_BACK`.
- Input modes: `MODE_INSERT`, `MODE_REPLACE`, `MODE_REPLACE_1`.

Declared helpers:
- Word classification and movement helpers.
- Character insertion/deletion primitives.
- Character editor lifecycle and buffer growth.
- Resize and alias callback installers.

Integration:
- Included by `el.h`, making character editing state part of the central `EditLine` object.
