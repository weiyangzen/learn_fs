# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_main.c

Top-level driver and diagnostics for the LTL translator.

Key responsibilities:
- Stores the active formula in static `uform[4096]`.
- Provides character stream functions used by lexer: `tl_Getchar`, `tl_peek`, and `tl_UnGetchar`.
- Initializes translator subsystems and parses `spin -f`-style options.
- Prints normalized formulas, full formulas in never-claim comments, and token explanations.
- Emits fatal parse diagnostics with caret location.

Important functions:
- `tl_main`: resets global translator state, parses `-f`, `-v`, `-n`, and `-c`, then calls `tl_parse`.
- `tl_balanced`: checks parentheses balance.
- `dump`: pretty-prints AST nodes.
- `Fatal`/`tl_yyerror`: report and exit on LTL errors.

Risks/quirks:
- Copies formula into fixed 4096-byte buffer with `strcpy`.
- `-n` normalizes and exits before automaton generation.
- `tl_out` is used for formula and never-claim output, allowing standalone or embedded operation.
