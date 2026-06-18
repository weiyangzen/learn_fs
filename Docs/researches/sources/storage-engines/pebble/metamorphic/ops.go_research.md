# sources/storage-engines/pebble/metamorphic/ops.go

## Purpose
`ops.go` defines the operation interface and all concrete operations replayed by the metamorphic harness. Each operation knows how to format itself, run against a `Test`, expose synchronization dependencies, rewrite its user keys for reduction/simplification, and provide diagram ranges.

## Important APIs, Types, and Functions
- `Ops`, `op`, `treeStepsOp`, `UserKey`, and `UserKeySuffix` define the shared operation model.
- Initialization and lifecycle operations: `initOp`, `newBatchOp`, `newIndexedBatchOp`, `batchCommitOp`, `closeOp`, `newSnapshotOp`, `newExternalObjOp`, `dbRestartOp`.
- Writer operations: `applyOp`, `deleteOp`, `singleDeleteOp`, `deleteRangeOp`, `flushOp`, `mergeOp`, `setOp`, `rangeKeyDeleteOp`, `rangeKeySetOp`, `rangeKeyUnsetOp`, `logDataOp`.
- Ingestion/replication operations: `ingestOp`, `ingestAndExciseOp`, `ingestExternalFilesOp`, `replicateOp`, `externalObjWithBounds`.
- Reader/iterator operations: `getOp`, `newIterOp`, `newIterUsingCloneOp`, `iterSetBoundsOp`, `iterSetOptionsOp`, `iterSeekGEOp`, `iterSeekPrefixGEOp`, `iterSeekLTOp`, `iterFirstOp`, `iterLastOp`, `iterNextOp`, `iterNextPrefixOp`, `iterCanSingleDelOp`, `iterPrevOp`.
- DB operations: `checkpointOp`, `downloadOp`, `compactOp`, `dbRatchetFormatMajorVersionOp`, `estimateDiskUsageOp`.
- Helpers include `formatOps`, `iterOptions`, `iteratorPos`, `validityStateToStr`, `onlyBatchIDs`, `closeIters`, `ingestOp.collapseBatch`, shared/external replicate helpers, and `hashSize`.

## Control Flow and State
Every `run` method retrieves objects from `Test`, calls the relevant Pebble API, and records a formatted outcome through `historyRecorder`. `formattedString` must be parseable by the metamorphic parser and stable across runs. `receiver` and `syncObjs` drive concurrent execution ordering: operations with the same receiver hash to the same thread, while additional dependencies prevent races with batches, DBs, snapshots, external objects, and newly created IDs.

Write operations use runtime test options to select variants such as `DeleteSized`, `SingleDelete` replacement, `ApplyNoSyncWait`, ingest-via-apply, excise simulation, shared/external replication, downloads disabled, and EFOS snapshots. Iterator operations serialize validity and position, including point value, range bounds, range keys, and `RangeKeyChanged`. Limit-based iterator operations map both exhausted and at-limit states to a deterministic `"invalid"` string.

Ingestion paths are complex. `ingestOp.run` either collapses a single batch and applies it, or builds local SSTs with blobs, closes batches, and calls `IngestAndExciseWithBlobs` without an excise span. `collapseBatch` reproduces ingest semantics by applying range deletions first, keeping only the latest point op per user key, and copying range keys verbatim from the batch. `ingestAndExciseOp` builds one ingest SST, optionally performs real `IngestAndExciseWithBlobs`, or simulates the excise through `DeleteRange` plus `RangeKeyDelete` before ingest.

External ingestion either emulates external-file ingest by building local truncated SSTs and calling `Ingest`, or constructs Pebble `ExternalFile` metadata with locator, object name, bounds, flags, and synthetic prefix/suffix. `replicateOp` scans a source DB over a span and either writes local SST contents for ordinary ingest after deleting destination range state, or preserves shared/external files through `ScanInternal` visitors and `IngestAndExcise`.

## State and Persistence Behavior
Operations mutate actual Pebble DBs, batches, snapshots, iterators, external storage, temporary SSTs, WALs, and histories. `initOp` sizes runtime object slots. `closeOp` clears `Test` object slots and flushes WAL-disabled DBs before close so kept data directories can seed later runs. Checkpoints write into `data/checkpoints/op-######`; ingest and replication create SST/blob files in test temporary storage; external-object creation writes remote SST objects.

## Dependencies and Integration Points
This file is the central integration layer with the Pebble public API, internal batch sorting, keyspan/rangekey internals, object storage providers, remote locators, VFS/errorfs, table writers, and treesteps. It consumes options from `TestOptions`, key formatting from `KeyFormat`, history recording, `Test` object accessors, retry policy, and generated fields computed after parsing/generation.

## Risks and Edge Cases
- `formattedString`, parser logic, and derived fields must stay in lockstep for reproducible reduce/compare workflows.
- Some API outcomes are nondeterministic by design; the code avoids recording nondeterministic return values for `CanDeterministicallySingleDelete` and normalizes iterator at-limit vs exhausted.
- Bounds slices passed to iterators are intentionally trashed after use to test Pebble's copying/lifetime assumptions.
- Checkpoint is no-op under shared/external storage because unsupported configurations would otherwise diverge.
- External object names include `rand.Uint64` to avoid collisions with initial state; formatted operation output does not include that object name, only the logical external object ID.
- Replication and excise no-op cases synthesize delete/range-key-delete behavior to preserve logical equivalence.

## Test Signals
`generator_test.go` and parser/reducer tests exercise formatting and generation. `options_test.go::TestBlockPropertiesParse` runs a small operation stream through `RunOnce`. Full metamorphic test suites are the primary coverage for the runtime behavior, with history diffs exposing divergence across option configurations.
