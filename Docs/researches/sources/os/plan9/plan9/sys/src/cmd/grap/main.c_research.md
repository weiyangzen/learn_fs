# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/main.c

This is the `grap` program driver. It parses `-d` debug and `-l` no-library flags, installs signal handlers, initializes defaults, then processes stdin or named files.

`getdata` copies normal input through unchanged, recognizes `.G1` blocks, emits `.PS`, runs `yyparse`, and closes with `.PE`. It preserves troff `.lf` line directives and updates the current filename/line state.

It uses a temp file for generated graph body output unless debugging directs output to stdout.
