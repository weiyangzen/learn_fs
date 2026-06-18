# sources/storage-engines/pebble/internal/dsl/dsl.go

## Purpose
`dsl.go` implements a generic parser for Pebble’s small lisp-like testing DSLs. It provides reusable scanner/parsing infrastructure for constants and parenthesized function calls.

## Important APIs, Types, And Functions
`NewParser[T]` creates a parser with constant and function registries. `NewPredicateParser[E]` creates a predicate parser preloaded with `Not`, `And`, `Or`, `OnIndex`, and `CallStackIncludes`. `Parser[T]` exposes `DefineConstant`, `DefineFunc`, `Parse`, and `ParseFromPos`. `Scanner` wraps `go/scanner.Scanner` with `Scan`, `Consume`, and `ConsumeString`. `Token` captures position, kind, and literal with a formatted `String`. `assertTok` panics on grammar mismatch.

## Control Flow
`Parse` trims input, initializes a Go scanner, parses one expression or constant through `ParseFromPos`, optionally skips one semicolon, and requires EOF. Parser errors are expressed as panics with `error` values and recovered into the returned `err`; non-error panics propagate.

## State And Persistence Behavior
Parser state is in-memory function/constant maps. Parsing produces caller-defined AST/value instances. There is no persistence, and no global registry.

## Dependencies And Integration Points
It depends on Go scanner/token packages, `strconv`, `strings`, and `cockroachdb/errors`. It is used by `internal/itertest` probe DSLs and predicate parsing in tests.

## Risks And Edge Cases
The grammar intentionally uses panics for control flow, so parse function authors must panic with `error` for user-facing parse failures. The parser accepts only constants or parenthesized calls and does not support arbitrary Go-like syntax. Duplicate definitions silently overwrite earlier map entries.

## Test Signals
Coverage is mostly indirect through `itertest` probe datadriven tests and `predicates_test.go`. Useful direct tests would cover unknown identifiers, string unquoting failures, trailing tokens, and semicolon handling.
