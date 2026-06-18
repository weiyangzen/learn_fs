# sources/storage-engines/pebble/metamorphic/key_manager.go

## Purpose
`key_manager.go` maintains generation-time metadata about keys, object histories, bounds, range-key usage, and single-delete eligibility. Its main job is preserving deterministic operation streams despite Pebble APIs whose results depend on user-level invariants, especially `SingleDelete` and ingest semantics.

## Important APIs, Types, and Functions
- `keyMeta` tracks one `(objID, key)` history; `keyHistory` and `keyHistoryItem` represent chronological write operations.
- `bounds` models inclusive or end-exclusive object key bounds with validation, overlap checks, and expansion.
- `keyManager` owns `byObj`, sorted global keys, global key maps, sorted prefixes, and prefix maps for a `KeyFormat`.
- `objKeyMeta` stores per-object key histories, object bounds, range tombstone/range-key flags, and range-key-set spans.
- Public-to-generator methods include `SortedKeysForObj`, `InRangeKeysForObj`, `KeysForExternalIngest`, `ExternalObjectHasOverlappingRangeKeySets`, `getSetOfVisibleKeys`, `addNewKey`, `checkForSingleDelConflicts`, `update`, `knownKeys`, `knownKeysInRange`, `prefixes`, `prefixExists`, and `eligibleSingleDeleteKeys`.
- Helpers `loadPrecedingKeys`, `opWrittenKeys`, and `insertSorted` seed later cross-version runs from prior ops.

## Control Flow and State
Each generated op is fed to `keyManager.update`. Point sets and merges append value operations. Deletes clear DB histories or append delete markers on batches. Range deletions are discretized over known keys in range and expand object bounds. Range-key operations expand bounds and set flags. Applies and commits merge batch metadata into the destination writer and remove source batch metadata. Ingests collapse batch histories first, skip state mutation for predicted overlapping-SST failures, and merge only successful source objects into the target DB.

Single-delete safety is modeled in two layers. `eligibleSingleDeleteKeys` enforces an object-local invariant by checking the tail of each key's history. `checkForSingleDelConflicts` evaluates whether merging a source object's history into a destination could expose more than one value before an unbounded single delete; generator code uses returned keys to insert regular deletes before the risky merge.

External ingestion logic transforms keys with synthetic prefixes/suffixes, restricts them to generated bounds, retains only one key per prefix for external-object construction, and checks for duplicate resulting keys. Synthetic suffix use is rejected when range delete/unset or overlapping range-key sets could create invalid logical conflicts.

## State and Persistence Behavior
The manager is an in-memory model of runtime persistence effects. It records only metadata needed for future generation, not values. Bounds approximate SST key coverage to predict ingest overlap failures. After `loadPrecedingKeys`, non-DB object metadata is discarded so subsequent runs retain previous DB state while avoiding conflicts with old transient object IDs.

## Dependencies and Integration Points
The manager consumes op structs from `ops.go`, `OpType` helpers, `KeyFormat` comparers, Pebble key ranges, and generator external-object metadata. It is called by `generator.add`, key generators for global-key registration, cross-version setup in `meta.go`, and tests. Its correctness is coupled to actual runtime semantics in `ops.go` for batch collapse, ingest, delete clearing, and external ingestion.

## Risks and Edge Cases
- Range deletions are approximated by known keys only; comments flag incomplete modeling for keys generated after a batch range deletion.
- `getSetOfVisibleKeys` uses unsafe conversion from map string keys to byte slices; callers must treat returned keys as read-only.
- `ExternalObjectHasOverlappingRangeKeySets` sorts `meta.rangeKeySets` in place, mutating stored order.
- Generation assumes `update` is called only for operations whose effects are predictable; runtime failures can invalidate manager state.
- Ingest collapse semantics must stay aligned with `ingestOp.collapseBatch`.

## Test Signals
`key_manager_test.go` checks key/prefix insertion, datadriven single-delete and bounds behavior, `opWrittenKeys` coverage for all method constructors, preceding-key loading, and random key-in-range generation. Generator tests and full metamorphic runs provide integration coverage.
