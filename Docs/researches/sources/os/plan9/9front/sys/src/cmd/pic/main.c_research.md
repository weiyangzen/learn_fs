# File Research: sources/os/plan9/9front/sys/src/cmd/pic/main.c

`main.c` is the top-level driver for the 9front `pic` troff preprocessor. It owns the global object, attribute, and text arrays, initializes default variables, installs the floating-point exception handler, defines the built-in `pid` macro, and processes input files or stdin.

The main scan loop passes ordinary input through unchanged, recognizes `.PS` blocks, optionally follows `.PS <file` inclusions, resets per-picture state, invokes `yyparse()`, computes picture dimensions from accumulated extrema, and emits `.PS`/`.PE` framed troff output through `openpl()`, `print()`, and `closepl()` when parsing succeeded. It also preserves troff `.lf` line directives.

Important state includes `curx/cury`, `hvmode`, `codegen`, bounding extrema, `PEstring`, and syntax/error counters. `reset()` frees prior objects, block symbol tables, and text strings before each picture, so downstream generators assume a fresh global state per picture.
