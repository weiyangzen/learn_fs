# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cb.c

Purpose: Implements `cb`, a C source beautifier/formatter.

Key points:
- Options: `-j` joins continued lines, `-s` strict formatting, `-l width` adjusts line width and maximum indentation.
- `work` is the main lexical/state machine. It tracks braces, parentheses, keywords, declarations, `if/else`, `do/while`, struct initializers, comments, strings, preprocessor lines, operators, and line splitting.
- Handles C and C++-style comments.
- Uses keyword and operator tables from `cb.h`.
- Uses character classification macros from `cbtype.h`.
- Maintains indentation stack `ind`, temporary lookahead buffer `temp`, output line buffer `string`, and state flags such as `keyflag`, `opflag`, `dolevel`, `structlev`, `paren`, and `question`.
- `getnext` performs lookahead across whitespace, comments, and preprocessor lines.
- `ptabs` folds deeply indented code after `maxtabs`.

Dependencies and interactions:
- Uses Plan 9 `<bio.h>` for input/output.
- Includes local `cb.h` and `cbtype.h`; links with `cbtype.c` for `_cbtype_`.
- Reads stdin or named files and writes formatted output to stdout.

Research notes:
- The formatter is not a parser; it is a token-aware state machine with extensive heuristics.
- Static fixed-size buffers drive behavior and impose limits on line and lookahead size.
