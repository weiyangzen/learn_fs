# File Research: sources/os/plan9/9front/sys/src/cmd/col.c

Implements `col`, a filter that eliminates reverse line feeds and handles half-line motion for terminal output streams.

It reads runes through `bio`, tracks current horizontal position and logical line/half-line position, stores a rolling page buffer of lines, and emits reordered output once lines are safe to flush.

Handles newline, NUL, escape sequences `ESC 7/8/9`, reverse line feed, carriage return, tab, backspace, space, and printable runes. `-b` changes overstrike behavior, `-f` treats half-line feeds as full movements, and `-x` suppresses tab compression on output.

The output path reconstructs spacing/tabs, backspaces, and half-line movement as needed.

Core data structures are fixed-size: `PL` page slots and `LINELN` line buffer.
