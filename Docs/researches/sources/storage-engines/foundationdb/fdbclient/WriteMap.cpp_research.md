# sources/storage-engines/foundationdb/fdbclient/WriteMap.cpp

Purpose: implements read-your-writes mutation tracking for transactions. `WriteMap` stores point operations and range metadata in a persistent tree, tracking cleared ranges, conflict ranges, unreadable ranges, and stacks of dependent atomic operations.

Important APIs and types: `OperationStack` manages a compact singleton-or-vector stack of `RYWMutation`s with `push`, `poppush`, equality, and `isDependent`. `WriteMap::mutate`, `clear`, `clearNoConflict`, `addConflictRange`, and `addUnmodifiedAndUnreadableRange` update the tree. `WriteMap::iterator` exposes segment classification and movement. `coalesce`, `coalesceOver`, and `coalesceUnder` fold atomic mutations using helpers from `Atomic.h`.

Control flow: point mutation first locates the containing segment via `scratch_iterator.skip(key)`, derives inherited clear/conflict/unreadable flags, then either inserts a new boundary or rewrites an existing entry. Independent sets replace prior readable operations; dependent atomic mutations are coalesced when possible and stacked when unsafe. Range clears remove covered tree entries and reinsert begin/end sentinels preserving conflict/unreadable transitions. Conflict-range addition rewrites affected boundaries so both key and following segment flags are marked conflicted.

State and persistence: state lives in a versioned persistent tree (`writes`, `ver`) plus an arena for copied keys/values. It is transaction-local, not durable by itself, but its entries drive commit mutation generation and conflict behavior.

Dependencies and integration: integrates `WriteMap.h`, `PTreeImpl`, `MutationRef`, `RYWMutation`, `KeyRangeRef`, `TraceEvent`, and atomic operation helpers. It is central to `ReadYourWrites` behavior.

Risks: correctness depends on boundary sentinels and paired flags (`is_*` vs `following_keys_*`). Non-associative atomic ops with mismatched operand sizes must not be incorrectly coalesced. Iterator invalidation is manually handled by clearing `it.tree` around tree edits.

Test signals: no tests in this file, but behavior is exercised through transaction/read-your-writes tests and atomic mutation tests. `dump()` provides trace diagnostics for segment state.
