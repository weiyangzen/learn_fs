# File Research: sources/os/plan9/9front/sys/src/cmd/spin/spinlex.c

`spinlex.c` is the lexer, inline expander, C-fragment collector, deferred LTL handler, and generated-C support module for Spin's front end. It feeds `spin.y` through `yylex`.

Key responsibilities:
- Tokenizes PROMELA source, including identifiers, strings, `$...$` LTL strings, character constants, numbers, comments, operators, optional semicolon insertion, preprocessor line directives, and scope tracking.
- Maps keywords and built-ins to yacc tokens through `Names`, and maps LTL words/operators through `LTL_syms`.
- Maintains source location globals `lineno`, `Fname`, `CurScope`, `scope_seq`, and `scope_level`.
- Implements inline definition capture with `prep_inline`, registration with `def_inline`, lookup with `find_inline`, expansion with `pickup_inline`, and nested inline stream reading through `getinline`/`uninline`.
- Preserves literal argument text for inline calls in `IArg_cont`, enabling textual substitution during expansion.
- Supports return-from-inline by translating `return expr` into assignment to the captured return target.
- Handles C fragments and declarations, including `c_code`, `c_decl`, `c_expr`, `c_state`, and `c_track`.
- Generates supporting verifier C code for embedded C state tracking: `gencodetable`, `c_add_sv`, `c_add_stack`, `c_add_def`, `c_add_globinit`, `c_add_locinit`, `plunk_c_decls`, `plunk_c_fcts`, and `plunk_expr`.
- Performs side-effect checks for `c_expr` used in logical contexts.
- Defers `ltl { ... }` formulas to a temporary file so they are parsed after the rest of the spec.
- Expands `select` statements into equivalent `if`/`do` source pushed back into the lexer stream.

Important interactions:
- `check_name` consults symbol/type/proctype/inline registries and performs inline formal-parameter substitution.
- `yylex` repairs common semicolon mistakes and keeps `owner` from leaking across statement boundaries.
- C-code support feeds later pangen modules by emitting state-vector declarations, hidden declarations, update/revert functions, and code lookup tables.

Notable details:
- Uses fixed-size buffers for inline text, parameter text, pushed-back select expansions, and generated C snippets.
- Deferred LTL uses `TMP_FILE2`.
- Scope names are encoded as underscore-prefixed numeric scope paths, later used by symbol lookup and disambiguation.
