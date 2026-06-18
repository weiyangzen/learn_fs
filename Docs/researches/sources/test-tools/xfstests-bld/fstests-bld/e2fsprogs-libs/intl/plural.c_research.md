# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural.c

Purpose: generated GNU Bison 1.35 parser for gettext plural expressions, built from `plural.y`.

Important APIs and control flow: the generated `yyparse` is renamed to `PLURAL_PARSE` outside glibc. It consumes a `struct parse_args *`, uses a pure-parser interface, and builds `struct expression` AST nodes through embedded `new_exp_*` helpers. The included scanner `yylex()` tokenizes numbers, variable `n`, `||`, `&&`, comparison, arithmetic, unary `!`, parentheses, and ternary `?:`, stopping safely at semicolon, newline, or NUL. `FREE_EXPRESSION()` recursively releases AST nodes.

State and persistence: parser state is stack/local; AST nodes are heap-allocated. No persistent state except generated parser tables. The caller owns the returned AST.

Dependencies and integration: includes `plural-exp.h`; used by `plural-exp.c` during catalog header parsing. It mirrors `plural.y`, so regeneration must use a compatible Bison skeleton.

Risks and test signals: generated code uses alloca/stack growth paths and old Bison conventions. Numeric token parsing can overflow `unsigned long` silently. Test representative plural expressions, invalid single `&`/`|`, malformed ternaries, allocation failures, and equivalence with regenerated output.
