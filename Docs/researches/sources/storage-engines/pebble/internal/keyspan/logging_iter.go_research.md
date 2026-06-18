# sources/storage-engines/pebble/internal/keyspan/logging_iter.go

## Purpose
Provides a debug wrapper that logs a whole `FragmentIterator` stack as a tree of operations and results.

## Important APIs, Types, And Functions
`WrapFn` is the recursive wrapper function type. `InjectLogging(iter, logger)` wraps all descendants using shared `loggingState`. `loggingIter` implements `FragmentIterator` and logs `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, and `Close`. `opStartf` manages nested treeprinter nodes.

## Control Flow
`InjectLogging` recursively calls `WrapChildren`, wrapping children before parents. Each operation creates a child log node, delegates to the wrapped iterator, records results, and, for top-level operations, emits formatted tree rows through the logger.

## State And Persistence Behavior
The wrapper keeps shared in-memory `treeprinter.Node` state and a logger reference. It does not persist data itself, but the supplied logger may write output.

## Dependencies And Integration Points
Depends on `base.Logger`, `treeprinter`, `treesteps`, and the `FragmentIterator.WrapChildren` contract. It is used for debugging iterator stacks and in logging tests.

## Risks And Edge Cases
Logging wrappers change allocation/timing and must preserve child semantics exactly. Recursive wrapping depends on all iterator implementations correctly forwarding `WrapChildren`.

## Test Signals
`logging_iter_test.go` verifies stable tree-shaped logs over a small stack after stripping pointer values.
