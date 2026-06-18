# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/lookup.c

This file implements eqn keyword, reserved-word, and definition tables.

Key responsibilities:
- Defines `keytbl`, `restbl`, and `deftbl` hash tables.
- Lists language keywords and maps them to yacc tokens.
- Lists reserved mathematical words/symbols and maps them to troff strings or Unicode Greek letters.
- Provides simple additive `hash`, `lookup`, and `install`.
- Initializes tables in `init_tbl`, then calls `init_tune`.

Important implementation notes:
- Keyword aliases include `integral` for `int`, `pile/lpile/cpile/rpile` for column forms, and `copy` for include.
- Reserved words cover relations, arrows, Greek letters, operators, and function names.
- Existing names are updated in place by `install`.
