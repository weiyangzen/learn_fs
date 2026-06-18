# sources/storage-engines/foundationdb/fdbclient/PartitionedLogIterator.h

## Purpose
`PartitionedLogIterator.h` defines the minimal reference-counted interface used to iterate partitioned mutation logs. It also defines `VersionedMutation`, the value object returned by the iterator, combining a database `Version`, a per-version `subsequence`, and a `MutationRef`.

## Important APIs, Types, and Functions
- `VersionedMutation` stores one mutation plus ordering metadata. Its arena-copy constructor deep-copies the `MutationRef` into the supplied `Arena`, while preserving version and subsequence.
- `PartitionedLogIterator` derives from `ReferenceCounted<PartitionedLogIterator>`, so callers generally hold it through `Reference<>`.
- `hasNext()` is a synchronous availability check.
- `peekNextVersion()` asynchronously exposes the next available version without consuming it.
- `getNext()` asynchronously returns a `Standalone<VectorRef<VersionedMutation>>`, making returned mutation batches self-owned through the standalone arena.

## Control Flow and State
This header contains no concrete iteration logic. Implementations are expected to maintain cursor state, answer `hasNext`, support version peeking, and advance on `getNext`. The interface separates cheap local availability from asynchronous storage or network reads.

## State and Persistence Behavior
The interface itself is in-memory only. Persistence belongs to the backing mutation-log implementation. `VersionedMutation`'s arena-aware copy is important because mutation refs are arena-backed and must remain valid after a batch crosses actor boundaries.

## Dependencies and Integration Points
The file depends on `fdbclient/FDBTypes.h` for `Version`, `MutationRef`, `Arena`, `VectorRef`, `Standalone`, `Future`, and reference counting. Consumers likely include backup, restore, or mutation-log readers that need ordered mutation replay across partitioned logs.

## Risks and Edge Cases
- Implementations must preserve ordering by `(version, subsequence)` across partitions, because this type exposes both fields but does not enforce ordering.
- `hasNext()` can race with asynchronous source changes unless implementers define stable cursor semantics.
- Returning refs without copying into the returned standalone arena would create lifetime bugs.

## Test Signals
Useful tests should cover empty logs, `peekNextVersion()` not consuming entries, arena lifetime of returned mutations, multi-mutation batches at the same version, and cross-partition ordering around subsequence boundaries.
