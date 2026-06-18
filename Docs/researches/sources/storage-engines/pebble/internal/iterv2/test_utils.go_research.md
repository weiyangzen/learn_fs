# sources/storage-engines/pebble/internal/iterv2/test_utils.go

## Purpose
`test_utils.go` provides randomized and scripted test utilities for `iterv2.Iter` implementations, including the differential checker used by random tests.

## Important APIs, Types, And Functions
`TB` abstracts `testing.TB`. `TestOp` enumerates operations and `TestOpWeights` weights them; `AllTestOps` is the default distribution. `CheckIterConfig` configures comparer, key generation, weights, operation count, and special prefix-change behavior. `CheckIter` runs random operations against a reference `TestIter` and implementation. `KeyGenConfig`, `RandKeyConfig`, `RandKey`, `RandPointKeys`, `RandSpans`, `RandBounds`, and `RunIterOps` support fixture generation and scripted execution.

## Control Flow
`CheckIter` creates a reference `TestIter` wrapped in `OpCheckIter` and wraps the implementation in `LoggingIter`. For each random operation, it builds an operation closure, runs it against the checker while catching `IllegalOpError`, skips illegal operations, runs the implementation, and compares returned key/trailer and span string. On panic or mismatch it logs the operation history.

## State And Persistence Behavior
All state is test-local. Random seeds are supplied by callers. `RunIterOps` formats output through a tabwriter but writes no files.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, `testkeys`, `crstrings`, `errors`, `rand/v2`, `slices`, `cmp`, `debug`, and formatting packages. It is shared by interleaving, single-span, trigger, and future iterv2 tests.

## Risks And Edge Cases
Comparing `Span.String()` is simple but can hide differences if formatting changes. Illegal-operation filtering depends on `OpCheckIter` correctness. Random generation must keep spans non-overlapping and keys internally sorted/deduplicated to satisfy iterator contracts.

## Test Signals
Mismatches produce high-signal operation logs and expected/actual span/key pairs. Passing random checks are strong evidence of semantic conformance over many operation sequences.
