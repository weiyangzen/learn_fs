# File Research: sources/os/plan9/9front/sys/src/cmd/vt/cons.h

## Role

`cons.h` declares shared terminal-emulator console state and screen/host I/O functions for the 9front `vt` command.

## Main Definitions

- `Consstate` tracks escape-state parser fields, argument buffer, saved cursor position, and key-state fields.
- Mode constants for newline/other and cooked/raw.
- Escape/parser state enum values such as base state, escape, CSI, OSC, charset, and title-related states.
- `ttystate` flags for ANSI and cursor-key behavior.
- `funckey` maps terminal key numbers to output strings, with external function-key tables for ANSI, application ANSI, VT220, and xterm modes.

## Declared Shared State

- Cursor and screen dimensions: `x`, `y`, `xmax`, `ymax`, `olines`.
- Parser state: `peekc`, `attribute`, `term`, `yscrmin`, `yscrmax`, `attr`, `defattr`.
- Color state: foreground/background images and normal/high color arrays.
- Runtime flags: `cursoron`, `nocolor`, and `bracketed`.
- OSC 7 current-directory buffer `osc7cwd`.

## Declared Operations

- Terminal emulation and input: `emulate()`, `host_avail()`, `nextchar()`, `sendnchars()`.
- Screen editing: `clear()`, `newline()`, `shift()`, `scroll()`, `backup()`, `drawstring()`.
- UI helpers: `ringbell()`, `pt()`, `pos()`, `funckey()`, `rewound()`, `setdim()`, and `mountcons()`.

## Notable Limitations And Risk Areas

- This header centralizes many globals used across `vt` implementation files, so state coupling is high.
- Multiple terminal behavior modes are selected by global tables and flags rather than per-instance objects.
- Correctness depends on implementation files keeping cursor bounds, scroll region, color state, and parser state synchronized.
