# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.y

Purpose: authoritative Bison grammar for gettext plural expressions.

Important APIs and control flow: it declares a pure parser with `YYLEX_PARAM` and `YYPARSE_PARAM` wired to `struct parse_args`. Grammar precedence follows C-like expression precedence for ternary, logical OR/AND, equality, comparison, additive, multiplicative, and unary not. Semantic actions allocate AST nodes with `new_exp_0` through `new_exp_3`; if allocation fails, children are freed and parsing aborts. The scanner recognizes decimal numbers, `n`, operators, parentheses, and end delimiters; `yyerror()` intentionally emits nothing.

State and persistence: no persistent state. It produces heap-owned `struct expression` trees and defines recursive `FREE_EXPRESSION`.

Dependencies and integration: generates `plural.c`; consumed by `plural-exp.c` via `PLURAL_PARSE`. Name mapping avoids symbol clashes across glibc/libintl/tool builds.

Risks and test signals: `%expect 7` documents known parser conflicts, so parser changes require careful conflict review. Test grammar associativity, malformed expressions, memory cleanup on partial failures, and compatibility between `.y` and checked-in generated `.c`.
