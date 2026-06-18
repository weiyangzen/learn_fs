# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_main.c

`tl_main.c` is the entry point and diagnostic shell for the LTL-to-Büchi translator embedded in Spin.

Key responsibilities:
- Defines TL global flags and counters: `newstates`, `tl_errs`, `tl_verbose`, `tl_terse`, `tl_clutter`, `state_cnt`, `All_Mem`, and `claim_name`.
- Stores the input formula in `uform` and provides character stream helpers `tl_Getchar`, `tl_peek`, and `tl_UnGetchar`.
- Checks parenthesis balance with `tl_balanced`, ignoring character/string literal parentheses.
- Initializes all TL subsystems in `tl_main`: Büchi state, cache, rewrite, and transition graph modules.
- Parses command-like arguments: `-f formula`, `-v`, `-n`, `-c claim_name`, and `-d`.
- Calls `tl_parse` to translate the formula.
- Prints formulas and nodes with `put_uform`, `dump`, and `tl_explain`.
- Emits fatal/syntax diagnostics with source-position caret display through `Fatal`, `tl_yyerror`, and `tl_non_fatal`.

Important interactions:
- `tl_out` is shared with `tl_buchi.c` for generated never-claim output.
- `tl_clutter` is selected based on xspin/trail mode to keep replay-generation compatible with verifier output.
- Memory/cache stats are printed only in verbose mode.
