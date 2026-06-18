# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/mod.rs

## Purpose
Implements simple write proposal batching and apply-side put, delete, delete-range, unsafe-write, and ingest integration for raftstore-v2.

## Important APIs, Types, And Functions
Re-exports `SimpleWrite`, `SimpleWriteBinary`, `SimpleWriteEncoder`, and `SimpleWriteReqDecoder`. Peer methods `on_simple_write`, `on_unsafe_write`, and `propose_pending_writes` coordinate proposal-side batching. Apply methods `apply_put`, `apply_delete`, and `apply_delete_range` modify tablets. The `ingest` submodule extends this with SST ingest.

## Control Flow
`on_simple_write` first amends an existing encoder if possible, otherwise validates command headers, deadline and disk-full options, drains pending writes to preserve order, delays behind conflicting admin proposals, rejects merge mode, and creates a new `SimpleWriteReqEncoder` bounded by raft entry size ratio. `propose_pending_writes` revalidates the encoder header, encodes batched data, proposes it, and posts callbacks. `on_unsafe_write` bypasses raft by sending an `ApplyTask::UnsafeWrite` to the local apply scheduler. Apply paths check log recovery skip state, validate keys against region bounds, update bucket write stats, prefix keys with data encoding, write/delete via default or named CF APIs, adjust size hints, and record per-CF modification indexes. Delete range validates bounds/CFs and schedules a tablet delete-range task unless `notify_only`.

## State And Persistence Behavior
Simple writes are persisted through raft, then applied into a tablet write batch that `command/mod.rs` flushes. Modification indexes track which data CFs changed at which raft index. Delete-range can perform asynchronous file/range deletion through the tablet worker and only records modifications when the worker reports data was written. Unsafe writes use `u64::MAX` indexes and force an apply flush need without raft durability.

## Dependencies And Integration Points
Depends on command validation/proposal logic, `ProposalControl`, disk-full policy, raftstore simple-write codec, tablet scheduler, engine CF helpers, bucket stats, apply flow control, and `ingest.rs` for SST writes.

## Risks And Edge Cases
Amending batched writes must keep a compatible header and size budget. Epoch-not-match proposals deliberately avoid calling proposed callbacks. Merge mode blocks normal writes. Delete-range must handle inclusive region end-key validation and invalid CF names. RocksDB/tablet APIs require prefixed data keys even though raftstore-v2 has isolated tablets.

## Test Signals
`test_delete_range` builds a test tablet, applies a put through committed entries, verifies the prefixed key exists, applies delete-range, and verifies removal. Additional signals are write command counters, failpoints after pending-write proposal and apply put, size-diff hints, and modification indexes.
