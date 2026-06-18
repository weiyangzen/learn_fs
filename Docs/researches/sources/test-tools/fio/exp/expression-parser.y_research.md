# sources/test-tools/fio/exp/expression-parser.y

## Purpose
`expression-parser.y` is the yacc grammar and evaluator for fio arithmetic expressions. It computes both integer and double results, tracks parse/value errors, and applies implied units when no explicit suffix appears.

## Important APIs, Types, And Functions
`struct parser_value_type` carries `dval`, `ival`, `has_dval`, and `has_error`; it is exposed as `PARSER_VALUE_TYPE`/`YYSTYPE`. Grammar tokens are `NUMBER`, `BYE` (unused), and `SUFFIX`. Operators include `+`, `-`, `*`, `/`, `%`, `^`, unary minus, parentheses, and suffix multiplication. Runtime support includes `lexer_input()`, `setup_to_parse_string()`, `evaluate_arithmetic_expression()`, and `yyerror()`.

## Control Flow
`evaluate_arithmetic_expression()` sets the lexer time-mode global, copies the input into a fixed double-null-terminated buffer, calls `yyparse`, restarts the lexer, and returns an error flag. The grammar reduces expressions by computing integer math when both operands are integral and double math otherwise. Suffix reduction multiplies the previous expression and sets `units_specified`. Division and modulo check for zero and flag errors through `yyerror`, while exponentiation handles integer positive powers directly and otherwise delegates to `pow()`. If no suffix was specified, the final value is multiplied by `implied_units`.

## State And Persistence
Parsing uses static `lexer_read_offset` and `lexer_input_buffer[1000]`, so it is explicitly not thread-safe. Inputs longer than the buffer are truncated. No persistent state is written.

## Dependencies And Integration Points
The grammar depends on the flex lexer, C math library `pow`, and generated yacc interfaces. It is called by the test program and likely by fio option parsing code that wants arithmetic in numeric options.

## Risks
Error handling is intentionally quiet: `yyerror()` does nothing, and some divide-by-zero reductions do not explicitly set `$$.has_error` beyond operand flags. Fixed buffer truncation can convert invalid long expressions into valid prefixes. Integer overflow is unchecked in arithmetic and suffix multiplication. Thread-unsafety is documented and material if expression evaluation is used concurrently.

## Test Signals
Tests should cover precedence/associativity, unary minus, suffix multiplication, implied units, time/non-time `m`, division/modulo by zero, exponent edge cases such as `0^0` and negative exponents, long input truncation, and integer overflow boundaries.
