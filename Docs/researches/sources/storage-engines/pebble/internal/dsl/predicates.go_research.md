# sources/storage-engines/pebble/internal/dsl/predicates.go

## Purpose
`predicates.go` defines reusable boolean predicate AST nodes and parse functions for the generic DSL parser.

## Important APIs, Types, And Functions
`Predicate[E]` requires `Evaluate(E) bool` and `String() string`. Constructors include `Not`, `And`, `Or`, `OnIndex`, and `CallStackIncludes`. `Index[E]` embeds `atomic.Int32` and fires only on its N-th invocation. Private implementations `not`, `and`, `or`, and `callStackIncludes` implement evaluation/stringification. Parse helpers include `parseNot`, `parseAnd`, `parseOr`, `parseOnIndex`, `parseVariadicPredicate`, and `parseCallStackIncludes`.

## Control Flow
Compound predicates evaluate children left to right, but `and` and `or` intentionally use boolean accumulation instead of short-circuiting, so every child predicate is evaluated. `OnIndex` atomically decrements and returns true when the new value is `-1`. `CallStackIncludes` captures up to 32 caller PCs and searches resolved frame function names for a substring.

## State And Persistence Behavior
Most predicates are immutable. `Index` is stateful and atomic, making repeated evaluation order significant and concurrency-safe at the counter level. No state is persisted.

## Dependencies And Integration Points
The file integrates with `NewPredicateParser` in `dsl.go` and `itertest` probe predicates. It depends on runtime stack inspection, `sync/atomic`, `go/token`, `strconv`, and `errors`.

## Risks And Edge Cases
Non-short-circuit evaluation matters for stateful predicates like `OnIndex`; this is useful for tests but can surprise callers. `CallStackIncludes` is fragile across function renames, inlining, and stack depth. `OnIndex(0)` fires on the first evaluation because decrement reaches `-1`.

## Test Signals
`predicates_test.go` validates call-stack matching. Indirect probe tests exercise parsed `And`, `Or`, `Not`, and `OnIndex` expressions.
