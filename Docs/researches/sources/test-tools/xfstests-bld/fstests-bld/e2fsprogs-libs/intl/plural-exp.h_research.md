# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/plural-exp.h

Purpose: defines the AST and parser interface for gettext plural-form selection.

Important APIs/types/functions: `struct expression` stores an operator, arity, and either numeric value or up to three child expressions. Operators cover variable `n`, constants, logical not, arithmetic, comparisons, logical and/or, and ternary `?:`. `struct parse_args` passes the input cursor and parse result through the Bison interface. Macros rename `FREE_EXPRESSION`, `PLURAL_PARSE`, `GERMANIC_PLURAL`, and `EXTRACT_PLURAL_EXPRESSION` for glibc, standalone libintl, or gettext-tool builds. Non-libintl/tool builds also expose `plural_eval`.

State and persistence: declares the global fallback expression and heap-expression ownership contract but stores no state itself.

Dependencies and integration: consumed by `plural-exp.c`, generated `plural.c`, grammar `plural.y`, and catalog loading code that evaluates plural forms.

Risks and test signals: ABI/name remapping is sensitive because `struct expression` is explicitly considered binary-incompatible across contexts. Test compile modes `_LIBC`, `IN_LIBINTL`, and tool builds; verify recursive free and parser result ownership.
