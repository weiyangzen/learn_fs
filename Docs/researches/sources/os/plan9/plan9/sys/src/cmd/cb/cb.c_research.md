# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cb.c

Plan 9 C beautifier main implementation. It reads stdin or named files and rewrites C source with indentation, spacing, newline, comment, preprocessor, string, block, `if/else`, `do/while`, `struct`, and operator handling.

Options are `-j` to join continuation lines, `-s` for stricter spacing, and `-l width` to set line width/folding thresholds. The formatter is a single-pass lexer/printer with lookahead buffering (`getnext`, `temp`, `inswitch`) and output buffering (`string`, `outs`, `putch`).

It relies heavily on globals from `cb.h`, keyword/operator tables, and classification macros from `cbtype.h`. It handles C and C++ comments, string/char escapes, nested brackets, preprocessor lines, ternary `?:`, and type/struct-specific formatting.
