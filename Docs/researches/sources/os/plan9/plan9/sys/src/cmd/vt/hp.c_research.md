# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/hp.c

This file implements an HP 2621-style terminal emulation, with `term = "2621"` and a local `fk[32]`.

Emulation behavior:
- Main loop reads characters through `get_next_char`.
- Handles null, bell, tab, backspace, newline, carriage return, and printable text.
- Escape handling supports HP-style cursor positioning, underline/standout toggles, home, insert/delete line, clear-to-end, delete char, insert mode, rolling scroll, and directional cursor movement.
- Printable text is batched in cooked mode when contiguous printable host data is available.
- Insert mode shifts existing line content to the right before drawing.
- Standout mode inverts the drawn rectangle.

Drawing dependencies:
- Uses old `ndraw` functions such as `xtipple`, `bitblt`, `string`, and `rectf`.

State:
- Tracks local `standout` and `insmode`.
- Uses shared cursor position, scroll, raw-mode translations, and screen geometry from `cons.h`.

Role:
- Alternate terminal emulator implementation sharing the same `main.c` substrate as the VT100 parser.
