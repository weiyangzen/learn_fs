# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/ldefs.h

Read fully: 181 lines, 4151 bytes. SHA-256 prefix: `01f36996af8d6595`.

This is the shared header for the Plan 9 `lex` implementation. It defines scanner-generator constants, token/tree node codes, default table sizes, packed-table feature flags, section identifiers, booleans, and all global variables used across `lmain.c`, `parser.y`, `sub1.c`, `sub2.c`, and `header.c`.

Major definitions include character count `NCH=256`, token/tree limits, regex node tags such as `RCCL`, `RSTR`, `RCAT`, `STAR`, `FINAL`, `S1FINAL`, and `S2FINAL`, and generated-table arrays such as `gotof`, `nexts`, `state`, `verify`, `advance`, and `stoff`.

Integration: it is the full internal ABI of the lexer generator. Most source files rely on shared globals rather than passing state.

Risk notes: static array limits are user-tunable through `%` directives, but allocation and overflow checks remain manual.
