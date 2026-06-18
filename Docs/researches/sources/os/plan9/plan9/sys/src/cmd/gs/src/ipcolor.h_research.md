# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipcolor.h

Interpreter-side Pattern color data header.

Key behavior:
- Defines `int_pattern`, holding the PostScript pattern dictionary ref.
- Defines `private_st_int_pattern()` GC descriptor macro for `zpcolor.c`.
- Declares `int_pattern_alloc`, which creates interpreter pattern client data from a pattern dictionary ref.

Research notes:
- The comment explains this is a structure rather than a ref array for the same GC/template reasons used by interpreter graphics state and font data.
