# File Research: sources/os/bsd/netbsd-src/lib/libintl/plural_parser.c

Hand-written tokenizer, recursive-descent parser, AST manager, and evaluator for gettext `Plural-Forms:` headers.

Supported expression grammar includes:
- identifiers, constants, parentheses
- unary `!`
- multiplicative, additive, relational, equality, logical AND/OR
- ternary conditional `?:`

The parser extracts `Plural-Forms:`, parses `nplurals=...;`, parses `plural=...;`, and returns an AST plus plural count. Runtime evaluation calculates the plural index for a given `n`.

Only identifier `n` is accepted in normal builds. Test builds can allow empty expressions and arbitrary identifiers. Public internal entry points are `_gettext_parse_plural`, `_gettext_calculate_plural`, and `_gettext_free_plural`.
