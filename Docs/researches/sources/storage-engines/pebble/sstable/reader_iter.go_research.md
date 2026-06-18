# sources/storage-engines/pebble/sstable/reader_iter.go

## Purpose
`reader_iter.go` defines the shared iterator interfaces, generic constraints, pool aliases, and invariant finalizers for SSTable point iterators. It also documents the key positioning and exhaustion invariants used by single- and two-level iterators.

## Important APIs, Types, and Functions
- `dataBlockIterator[D]` constrains embedded data block iterators to `blockiter.Data` plus metadata-returning variants and a pointer-to-`D` shape.
- `indexBlockIterator[I]` constrains embedded index iterators to `blockiter.Index` plus pointer-to-`I`.
- `Iterator` extends `base.InternalIterator` with `NextPrefix` and `SetCloseHook`.
- Type aliases instantiate single-level and two-level iterators for row blocks and column blocks.
- Four `sync.Pool` values recycle row/column single/two-level iterator instances.
- `init` initializes pools and optional invariant finalizers.
- `checkSingleLevelIterator` and `checkTwoLevelIterator` finalizers detect leaked block handles.

## Control Flow
The long package comment is part of the functional contract: it defines bounds-exhausted, data-exhausted, local vs global exhaustion, and the safe conditions for monotonic-bounds and `TrySeekUsingNext` optimizations.

At initialization, each pool constructs the appropriate iterator type, stores a pool pointer, and when invariant finalizers are enabled registers a finalizer that checks embedded data and index block handles are not still valid. The finalizer prints to stderr and exits on leaked handles.

The checker functions cast pooled objects back to concrete generic iterator types and inspect `Handle().Valid()` on embedded data/index iterators. The two-level checker inspects the embedded second-level single-level iterator.

## State and Persistence Behavior
This file manages in-memory iterator lifecycle, not persisted data. Pooling means iterator structs retain some fields across uses unless reset by close logic, so the reset boundary in `reader_iter_single_lvl.go` and two-level code must stay synchronized with fields added here and there.

The documented exhaustion state is critical persistent-read behavior: incorrect exhaustion tracking can skip or duplicate keys while reading immutable SSTables, especially when bounds, block-property filters, and direction changes interact.

## Dependencies and Integration Points
- Integrates with `base.InternalIterator`, `blockiter`, `rowblk`, and `colblk`.
- Pool aliases are used by `reader.go` constructors and single/two-level iterator implementations.
- Finalizers depend on `internal/invariants` and are intended for debug/test builds.
- `SetCloseHook` supports file-cache reference counting around `Reader` lifetimes.

## Risks and Edge Cases
- The optimization invariants are subtle; conflating bound exhaustion with data exhaustion previously caused bugs, and future changes must preserve the distinction.
- Pool reuse plus generics requires careful zeroing and handle closure, or old state/read handles can leak into new iterator uses.
- Finalizer failures exit the process, which is appropriate for invariant builds but severe if accidentally enabled in inappropriate environments.
- `NextPrefix` is a Pebble extension beyond `InternalIterator`; wrappers must preserve it when adapting iterators.

## Test Signals
`reader_iter_test.go` exercises lazy-loading lifecycle, resource cleanup, bloom-filter preservation, and concurrent iterator use. `random_test.go` stresses the documented positioning invariants under many operations and injected errors. `reader_iter_treesteps_test.go` validates tree-step introspection over iterator trees.
