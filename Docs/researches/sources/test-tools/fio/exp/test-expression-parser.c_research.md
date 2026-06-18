# sources/test-tools/fio/exp/test-expression-parser.c

## Purpose
`test-expression-parser.c` is an interactive command-line harness for the experimental arithmetic expression parser. It reads expressions from stdin, evaluates them, and prints integer and double results.

## Important APIs, Types, And Functions
The program includes generated `y.tab.h` and declares `evaluate_arithmetic_expression()`. `main()` owns a fixed 100-byte input buffer, calls `fgets`, strips a trailing newline, invokes the evaluator with implied units `1.0` and non-time mode, and prints either `"%lld (%20.20lf)"` or `Syntax error`.

## Control Flow
The loop continues until `fgets` returns NULL. The `bye` variable is initialized to zero and never changed, so EOF is the only exit. On parse success, both integer and double results are displayed; on parse failure, the local result variables are reset.

## State And Persistence
No persistent state exists. The parser itself uses static lexer/parser state in the generated files.

## Dependencies And Integration Points
This file depends on the expression parser build products and C stdio/string APIs. It is a developer/test utility rather than a fio runtime component.

## Risks
Input is limited to 89 characters plus terminator by `fgets(buffer, 90, stdin)`, which may split longer expressions across iterations. The unused `bye` variable suggests an abandoned command feature. The harness always uses non-time mode and implied units of 1.0, so it does not exercise all evaluator modes.

## Test Signals
Use it for smoke testing arithmetic, suffixes, and syntax errors. Automated tests should feed representative expressions over stdin and compare stdout/stderr. Additional harness coverage would be needed for `is_time=1` and non-1 implied units.
