<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/dsl.go -->
# sources/storage-engines/pebble/vfs/errorfs/dsl.go

## Purpose
Provides the public predicate helpers and parser for `errorfs`'s Lisp-like error-injection DSL. It lets tests express when to inject an error or latency by operation class, path glob, operation offset, call stack, logical invocation index, boolean composition, or deterministic randomness.

## Important APIs, Types, and Functions
`Predicate` aliases `dsl.Predicate[Op]`. `And`, `Not`, `PathMatch`, `CallStackIncludes`, `OpKindIn`, `Randomly`, and `ParseDSL` are the main construction/parsing entry points. `NewParser` wires constants like `Reads`, `Writes`, `OpFileWrite`, functions like `PathMatch`, `OpFileReadAt`, `Randomly`, and the default `ErrInjected` labelled error. `Parser.AddError` allows tests to register additional `LabelledError` values. `LabelledError` implements both `error` and `Injector`, returning a stack-wrapped error if its optional predicate matches.

## Control Flow
Programmatic helpers construct predicate objects whose `Evaluate` methods inspect an `Op`. `ParseDSL` delegates to the package-level parser. During parser construction, predicate grammar and injector grammar are registered separately; a labelled error is both a constant injector and a function that parses a trailing predicate. `parseRandomly` validates probability and optional seed, while `parseFileReadAtOp` parses an exact read offset.

## State and Persistence Behavior
The DSL has no filesystem persistence. Stateful behavior is limited to deterministic pseudo-random predicates: `Randomly` embeds a `keyedPrng` so each path has its own PRNG sequence derived from a root seed. Parser instances keep grammar tables and may be extended with labelled errors.

## Dependencies and Integration Points
Depends on `internal/dsl` for generic scanners, parsers, predicates, boolean composition, call-stack predicates, and `OnIndex`. It integrates with `errorfs.Op`/`OpKind` from `errorfs.go` and `RandomLatency` parsing from `latency.go`. Tests in WAL failover and VFS failure paths feed DSL strings through `errorfs.ParseDSL`.

## Risks and Edge Cases
Invalid path globs panic during evaluation, so test DSL mistakes fail hard. `Randomly` rejects probabilities greater than 1 but negative values are syntactically impossible under the current scanner behavior. Call-stack matching is intentionally fragile under renames. `LabelledError.MaybeError` stack-wraps itself, so consumers should use `errors.Is` rather than string matching.

## Test Signals
`errorfs_test.go` drives the DSL parser through datadriven `parse-dsl` cases. Failover manager/writer tests also parse injected-error DSL strings, giving integration coverage for path, operation, and error predicates.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/dsl.go -->
