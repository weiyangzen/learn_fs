# sources/storage-engines/pebble/metamorphic/generator.go

## Purpose
`generator.go` builds the randomized operation stream consumed by Pebble's metamorphic tests. It owns generation-time object lifetimes, random operation selection, iterator option mutation, key distribution calls, DB/batch/snapshot/external-object relationships, and deterministic cleanup operations. The generator deliberately constrains some random choices so replay remains comparable across many Pebble option configurations.

## Important APIs, Types, and Functions
- `GenerateOps(rng, n, kf, cfg) Ops` is the public entry point for producing an `Ops` slice from a `KeyFormat` and `OpConfig`.
- `generator` stores `cfg`, `rng`, `init`, generated `ops`, `keyManager`, `keyGenerator`, live object sets, object-to-DB maps, reader/iterator maps, snapshot bounds, iterator last options, and cached visible-key sets for prefix seeks.
- `iterOpts` and `iterFlags` model generated iterator bounds, key-type modes, masking suffixes, point suffix filters, L6 filter enablement, and maximum-suffix property use. `IsZero` and `String` preserve clone/default-option formatting behavior.
- `generate` maps `OpType` weights to generator methods, draws from `randvar.NewDeck`, appends final close operations through `dbClose`, and calls `computeDerivedFields`.
- Object lifecycle methods include `newBatch`, `newIndexedBatch`, `removeBatchFromGenerator`, `batchAbort`, `batchCommit`, `dbClose`, `dbRestart`, `newIter`, `newIterUsingClone`, `iterClose`, `newSnapshot`, `snapshotClose`, and `newExternalObj`.
- Writer/read operation generators include point writes, range tombstones, range keys, log data, apply/commit, ingest, ingest-and-excise, external file ingestion, gets, iterator movement, checkpoints, compactions, downloads, flushes, format ratchets, estimates, and replication.
- Utility methods `prefixKeyRange`, `generateDisjointKeyRanges`, `uniqueKeys`, `expRandInt`, `cmp`, `prefix`, and `resizeBuffer` support sorted valid key spans and low-allocation key construction.

## Control Flow and State
Generation starts with `initOp`, one or more DB IDs, and DBs in both `liveReaders` and `liveWriters`. Each generated operation is appended through `add`, which immediately updates `keyManager` so future generation has the expected key state. Random op choice uses a weighted deck, not independent draws, giving balanced TPCC-style operation coverage.

The live-object sets are the central safety mechanism. Batches are writers, indexed batches are readers and writers, snapshots are readers, and iterators are attached to readers. Closing or applying a batch removes it from all live sets and closes its iterators. Snapshot close similarly removes child iterators. `dbRestart` and final `dbClose` drain iterators, snapshots, and batches before closing/restarting DBs.

Iterator generation snapshots the reader's visible keys at creation time for better `SeekPrefixGE` target selection. `mutateOptions` and `iterSetOptions` vary bounds, key types, masking, suffix filters, L6 filters, and maximum-suffix properties while forcing a subsequent absolute positioning operation because relative iterator movement after `SetOptions` requires re-positioning. Bounded snapshots constrain iterator bounds and gets to generated disjoint spans.

Writer operations coordinate with `keyManager` to preserve user-level determinism. Single deletes are only generated for keys that the manager considers eligible. Applying, committing, ingesting, ingest-and-excising, or external-ingesting a batch may first synthesize point `Delete` operations for keys whose single-delete history would otherwise become nondeterministic after merging histories into the destination.

## State and Persistence Behavior
This file does not execute Pebble persistence itself; it emits operation objects that later do. It still models persistent effects at generation time through `keyManager.update`, object bounds, and object-to-DB association. External objects are represented as generated `externalObjTag` IDs after converting a batch into a reusable external SST object. Ingest and replication choices account for whether generated SST bounds overlap because failed ingestions must not mutate generation-time state.

## Dependencies and Integration Points
The generator depends on `ops.go` op structs and `OpType` values, `key_manager.go` for write history and eligible keys, key-format implementations for random keys and suffixes, `options.go` format-version constants, and parser-derived-field logic for replay. It imports Pebble APIs for key ranges and iterator key type constants, `sstable` for synthetic prefix/suffix metadata, `randvar` for deck distributions, and `base.Compare` utilities.

## Risks and Edge Cases
- The generation-time model must match runtime behavior closely; any operation that can fail after `keyManager.update` would desynchronize later single-delete and ingest decisions.
- Range delete tracking is discretized over known keys; comments note that batch range deletions may not cover keys generated later.
- External-file synthetic suffixes are disallowed when range deletes, range-key unsets, or overlapping range-key sets would make transformed keys ambiguous.
- Iterator bounds passed to eventually-file-only snapshots must remain within snapshot consistency ranges.
- `uniqueKeys` can panic after many failed attempts, so key generators must have enough keyspace.
- Multi-instance runs require same-DB batch applies and special config limitations.

## Test Signals
`generator_test.go` directly checks live-object bookkeeping for batches, indexed batches, snapshots, iterators, applies, and aborts; deterministic generation from the same seed; non-overlap from `generateDisjointKeyRanges`; and Cockroach suffix keyspace round-tripping. `key_manager_test.go` indirectly tests generator assumptions around preceding-key loading and single-delete conflicts.
