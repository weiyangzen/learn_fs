# File Research: sources/os/plan9/9front/sys/src/cmd/grap/main.c

Program entry for `grap`. It installs interrupt/FPE handlers, parses `-d` debug and `-l` no-library flags, initializes defaults, and processes stdin or named files. It scans for `.G1` starts, maps them to `.PS`, runs `yyparse`, emits `.PE`, and otherwise copies input through.

It manages a temporary file for generated pic content, line directives, default variables (`frameht`, `framewid`, `ticklen`, `slop`), cleanup on interrupt, and dynamic buffer growth.
