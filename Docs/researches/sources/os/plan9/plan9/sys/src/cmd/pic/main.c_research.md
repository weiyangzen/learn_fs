# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/main.c

Main driver for the classic `pic` preprocessor. It initializes globals, defaults, object/text/attribute arrays, a predefined `pid` macro, and processes stdin or file arguments.

`getdata` copies normal troff input through unchanged, detects `.PS` blocks, optionally includes external picture files via `.PS <file>`, runs the parser, computes picture dimensions, emits troff output if no syntax errors occurred, and handles `.lf` line directives.

Defaults include scale-sensitive dimensions for line, move, box, circle, arc, ellipse, arrow, text, max page size, and fill value. Changing `scale` recalculates scalable defaults.

`reset` frees previous picture objects, block symbol tables, and text strings, resets cursor/direction/bounds, and prepares for the next `.PS` block.
