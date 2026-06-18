# sources/storage-engines/pebble/internal/iterv2/iter.go

## Purpose
`iter.go` defines the `iterv2.Iter` contract: a point iterator augmented with span partition information and synthetic boundary keys.

## Important APIs, Types, And Functions
`Iter` embeds `base.InternalIterator` and adds `Span() *Span`. `BoundaryType` enumerates `BoundaryNone`, `BoundaryEnd`, and `BoundaryStart`. `Span` exposes one boundary direction and sorted `keyspan.Key`s. `Span.Valid` and `Span.String` provide state checks and formatted output.

## Control Flow
This file is mostly contract documentation. It specifies how keyspace is partitioned into spans, when boundary keys are emitted, what `Span` means at boundaries, how prefix iteration exposes boundaries, the legal conditions for `TrySeekUsingNext`, and when `NextPrefix` is legal.

## State And Persistence Behavior
The interface requires implementations to return a stable pointer to embedded span state that updates across operations. Boundary can be nil for unbounded edges. No persistence exists in this file.

## Dependencies And Integration Points
It depends on `base`, `keyspan`, and `strings`. Implementations include `InterleavingIter`, `SingleSpanIter`, `TestIter`, `TriggerIter`, wrappers like `LoggingIter`, `InvalidatingIter`, and `OpCheckIter`.

## Risks And Edge Cases
The contract is intentionally subtle around boundary keys, prefix seeks, and `TrySeekUsingNext`. Implementations must expose range deletion spans even when no point key with the prefix exists. Boundary keys use `SeqNumMax`, affecting ordering with same-user-key point keys.

## Test Signals
The `iterv2` test utilities use this contract as the oracle: `OpCheckIter` enforces legal operations, `TestIter` models expected outputs, and random tests compare implementations against it.
