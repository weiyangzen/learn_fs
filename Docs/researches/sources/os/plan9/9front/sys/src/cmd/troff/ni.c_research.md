# File Research: sources/os/plan9/9front/sys/src/cmd/troff/ni.c

Read completely: 389 lines, 8475 bytes.

Global data definition file for troff/nroff. It instantiates most variables declared in `ext.h`, including built-in registers, request table, initial environment, buffers, flags, special character slots, and indirect function pointers.

Key contents:
- Initial `Numtab` entries for page number, line, date, time, and status registers.
- `contab` maps two-character request names to handlers such as `.ds`, `.sp`, `.ft`, `.if`, `.bp`, `.br`, `.so`, `.hy`, `.cf`, and many more.
- Initial `Env env[NEV]` sets default fill, adjust, font, point size, control characters, hyphenation, tab, line, and word state.
- Defines stacks, diversions, trap arrays, page lists, translation table, buffers, special-name table, and runtime-dispatch function pointers.

Reliability notes:
- This file is the shared mutable backbone of the formatter; initialization order with `n1.c` matters.
