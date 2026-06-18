# File Research: sources/os/plan9/9front/sys/src/cmd/troff/fns.h

Read completely: 379 lines, 7219 bytes.

Function prototype hub for troff/nroff. It declares routines from input handling, output, macro/string management, registers, requests, line filling, hyphenation, drawing, terminal output, font loading, and nroff/troff-specific implementations.

Key contents:
- Prototypes for `n1.c` through `n10.c` request handlers and helpers.
- Troff-specific `t6.c`, `t10.c`, and `t11.c` declarations.
- Nroff-specific `n6.c` and `n10.c` declarations.
- Indirect function pointer externs used to dispatch through `TROFF`/`NROFF`, such as `width`, `setch`, `ptout`, `setfont`, `vmot`, and `hmot`.

Dependencies:
- Included by most troff/nroff source files after `tdef.h`.

Reliability notes:
- The header reflects a large C89-style shared program, including some legacy untyped declarations elsewhere in the implementation.
