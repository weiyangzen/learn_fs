# sources/storage-engines/sqlite/test/lemon-test01.y

## Purpose

`lemon-test01.y` is a historical Lemon parser-generator testcase for parser error recovery and lifecycle callbacks. The header states it became obsolete after SQLite check-in `7cca80808cef192f` on 2021-08-17 and no longer works, so it is retained as reference material rather than active expected-pass coverage.

## Important APIs, Types, and Grammar Elements

It uses Lemon directives `%token_prefix TK_`, `%token_type int`, `%default_type int`, `%include`, `%syntax_error`, `%parse_accept`, `%parse_failure`, and `%code`. The grammar is `all ::= A B.` plus `all ::= error B.`. The embedded C expects generated APIs `ParseInit()`, `Parse()`, `ParseFinalize()`, `yyParser`, and token macros from `lemon-test01.h`.

## Control Flow

Generated callback actions increment global counters for syntax errors, accept, and failure. Embedded `main()` feeds three token sequences: valid `A B`, recoverable `B B`, and invalid `A A`. It then checks expected counter values through `testCase()`.

## State and Persistence Behavior

There is no persistence. State is limited to generated parser stack state and process-global counters.

## Dependencies and Integration Points

It is consumed by Lemon via `lemon lemon-test01.y && gcc -g lemon-test01.c && ./a.out`. It depends on generated parser files and standard C `assert.h`. It documents a parser-generator behavior boundary rather than SQLite runtime behavior.

## Risks and Test Signals

Because it is obsolete, current failure may be expected. The third test reuses IDs `200`, `210`, and `220`, making output less distinct. Historical success was nine `ok` lines and a final all-tests-pass message.
