# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/fns.h

Function prototype hub for troff/nroff.

Key responsibilities:
- Declares prototypes for initialization, input, control dispatch, output, macro/string storage, number registers, request handlers, text layout, hyphenation, drawing, device output, font loading, and nroff-specific routines.
- Declares the indirect function pointers selected by troff or nroff initialization.
- Groups functions by historical source modules (`c1.c`, `c3.c`, etc.) even though this tree uses `n*.c` and `t*.c` names.

Important behavior:
- Includes prototypes for both troff and nroff implementations, including many functions not in this group.
- Carries legacy declarations for non-standard C library functions used by the program.
- Acts as the compile-time connection point for the whole formatter.

Notable risks:
- Some declarations preserve old K&R-era assumptions and names.
- Several prototypes correspond to functions whose implementations are outside this grouped batch, so changing signatures here has broad impact.
