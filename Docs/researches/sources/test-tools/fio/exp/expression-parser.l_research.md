# sources/test-tools/fio/exp/expression-parser.l

## Purpose
`expression-parser.l` is the flex lexer for fio arithmetic expressions used by the experimental expression parser. It tokenizes numeric values, arithmetic operators, comments, whitespace, and fio-style unit suffixes.

## Important APIs, Types, And Functions
The lexer includes `y.tab.h`, defines `YYSTYPE` as `PARSER_VALUE_TYPE`, and overrides `YY_INPUT` to read from parser-provided `lexer_input()`. It exports global `lexer_value_is_time`, which decides whether suffix `m` means mebibytes or minutes. The `set_suffix_value` macro fills both integer and double values plus flags in `yylval`.

Rules recognize binary and decimal byte suffixes, time suffixes (`us`, `ms`, `s`, `m`, `h`, `d`), floating/scientific numbers, hex numbers, integers, arithmetic operators, newlines, and invalid characters. Comments and everything after `#`, `:`, or `,` are ignored.

## Control Flow
Flex scans the current expression string supplied by `lexer_input`. Suffix tokens return `SUFFIX` with multiplier metadata. Number tokens parse via `sscanf` and return `NUMBER`, setting `has_dval` when fractional/scientific syntax is used. Operators return their character code directly for yacc precedence handling. Newline returns 0 to end parsing.

## State And Persistence
The lexer is not thread-safe: it uses global `lexer_value_is_time` and yacc/flex globals. It stores no durable state.

## Dependencies And Integration Points
It depends on the yacc grammar's `PARSER_VALUE_TYPE`, `NUMBER` and `SUFFIX` tokens, `yyerror`, and parser-supplied input. It is paired with `expression-parser.y`.

## Risks
Some suffix values look suspicious: `[tT]` multiplies the integer by 1 TiB but the double by 1024^5, while `[pP]` uses the same integer expression as T but a larger double. Decimal IEC-looking suffixes such as `KiB` map to 1000 rather than 1024, which may be intentional or inverted naming. Integer parsing uses `int`, so large bare integers/hex values can overflow before being stored as `long long`.

## Test Signals
Lexer tests should cover every suffix in both time and non-time modes, fractional/scientific numbers, hex values, comments after separators, invalid characters, large numeric overflow behavior, and operator tokenization.
