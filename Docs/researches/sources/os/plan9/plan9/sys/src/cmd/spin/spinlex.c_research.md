# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/spinlex.c

This file implements Spin’s lexer, inline expansion machinery, embedded C-code capture, C-state tracking support, and token name tables.

Lexer/global state:
- `lineno`, `Fname`, `yytext`, `yyin`, `yyout`.
- Scope tracking via `scope_seq`, `scope_level`, and `CurScope`.
- Inline expansion stacks with `MAXINL`, `MAXPAR`, and `MAXLEN`.
- `IType` records inline/C-code definitions with body text, formal parameters, call/definition source locations, preconditions, and unique inline ids.
- `C_Added` records `c_state` and `c_track` declarations.

Lexing:
- `lex()` skips whitespace/comments, handles preprocessor line directives, strings, `$...$` LTL strings, character constants, numbers, names, LTL operator spellings, comments, multi-character operators, and scope entry/exit.
- `check_name()` maps keywords and LTL symbols, converts mtype names to constants, recognizes `_last`, handles inline actual-parameter substitution, and returns `UNAME`, `PNAME`, `INAME`, or `NAME`.
- `yylex()` wraps `lex()` to repair common semicolon mistakes around `}` and `else`, and records inline actual parameter text while parsing inline calls.

Keyword tables:
- `Names[]` maps Promela keywords and type names to parser tokens and type values.
- `LTL_syms[]` maps textual LTL operators when `ltl_mode` is active.

Inline and C embedding:
- `prep_inline()` captures inline or C-code body text, handles optional preconditions for `c_code`, records source line directives, and stores definitions through `def_inline()`.
- `pickup_inline()` pushes an inline body on the inlining stack and validates actual/formal parameter counts.
- `getinline()` and `uninline()` feed inline body text into the lexer as if it were source input.
- `plunk_expr()`, `plunk_inline()`, `plunk_c_decls()`, and `plunk_c_fcts()` emit captured C fragments into generated verifier code.
- `no_side_effects()` does textual checks to reject obvious side effects in `c_expr`.

C state tracking:
- `c_state()` and `c_track()` record externally managed C objects.
- `c_preview()`, `c_add_sv()`, `c_add_stack()`, `c_add_def()`, `c_add_globinit()`, `c_add_locinit()`, and `c_add_loc()` generate state-vector fields and update/revert/stack helper functions for generated pan code.

Risk notes:
- Inline parameter substitution is textual and includes explicit checks for cyclic replacement and struct-field substitution hazards.
- Many buffers are fixed-size (`yytext[2048]`, inline body buffers, parameter text buffers).
- C-expression side-effect detection is heuristic and cannot catch all effects through function calls.
