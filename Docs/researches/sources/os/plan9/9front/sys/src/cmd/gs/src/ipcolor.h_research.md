# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ipcolor.h

Interpreter header for Pattern color client data.

Key contents:
- Defines `int_pattern`, storing the original pattern dictionary ref.
- Defines `private_st_int_pattern`, the GC descriptor macro for the pattern client-data struct.
- Declares `int_pattern_alloc`, which creates interpreter pattern data from a PostScript object.

Notable dependencies:
- Uses `ref` and Ghostscript memory/structure descriptor types from surrounding interpreter headers.

Research notes:
- The comment explains that this is a structure rather than a ref array for the same reasons used by graphics state and font data.
- This header is paired with pattern-color implementation code such as `zpcolor.c`.
