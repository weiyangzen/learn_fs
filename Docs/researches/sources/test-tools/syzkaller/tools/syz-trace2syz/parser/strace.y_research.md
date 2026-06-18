# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.y

## Purpose
This goyacc grammar is the authoritative source for the generated strace parser used by `syz-trace2syz`.

## Important APIs, types, and functions
- `%union` defines semantic fields for strings, integers, constants, IR values, type slices, groups, buffers, and syscalls.
- Tokens describe strace literals, identifiers, flags, date/time/MAC/IP-like strings, numeric values, punctuation, operators, `UNFINISHED`, `RESUMED`, and null/question values.
- `syscall` productions create `NewSyscall` values for normal, paused, resumed, question-return, flagged-error, parenthetical-return, and PID-prefixed forms.
- `constant` productions evaluate arithmetic/bitwise expressions at parse time.
- `group_type`, `field_type`, and `buf_type` map strace aggregates and named fields to IR values.

## Control flow
A parsed line starts at `syscall`. Grammar actions assign `Stracelexer.result` as soon as a complete syscall form is recognized. Resumed fragments are represented as temporary calls with `Resumed=true`; later `Trace.add` merges them into the previous paused call. Field forms generally keep the right-hand value, except arrows keep the left-hand value.

## State and persistence behavior
No persistent state. Grammar actions mutate only the current parser semantic value and concrete lexer result. Constants are folded into `parser.Constant` during parsing.

## Dependencies and integration points
Consumes tokens from `lex.go` and constructs IR types from `intermediate_types.go`. Regeneration produces `strace.go`. `parser.go` calls the generated parser per input line.

## Risks and edge cases
The grammar accepts a pragmatic subset of strace, so unsupported output forms abort parsing. Some tokens, such as signal/date/MAC/IP forms, are tokenized but not all are semantically used in every context. Arithmetic uses unsigned `Constant`, so negative/underflow behavior is intentional but surprising. Concrete lexer type assertions in actions constrain parser reuse.

## Test signals
`parser_test.go` covers many productions, including paused/resumed calls, return variants, expression folding, groups, and PIDs. More grammar-level coverage is needed for strings, field assignments, signals, MAC/IP/date tokens, and parse errors.
