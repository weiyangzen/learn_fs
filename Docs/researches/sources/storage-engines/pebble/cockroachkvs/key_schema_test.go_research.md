<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/key_schema_test.go -->
# sources/storage-engines/pebble/cockroachkvs/key_schema_test.go

## Purpose
Additional key-schema tests focused on full `colblk.DataBlockEncoder`/`DataBlockIter` behavior, datadriven block descriptions, suffix-type headers, seeking, and random serialized engine keys.

## Important APIs, Types, and Functions
`TestKeySchema` runs datadriven files `suffix_types`, `block_encoding`, and `seek`. `runDataDrivenTest` supports `init`, `describe`, `suffix-types`, `keys`, and `seek`. `TestKeySchema_RandomKeys` generates random serialized engine keys. `randomSerializedEngineKey` creates keys with possible no-version, wall, logical, synthetic, or lock-table version lengths.

## Control Flow
The datadriven harness initializes an encoder and iterator, parses internal KVs, adds them with `KeyWriter.ComparePrev`, verifies `MaterializeLastUserKey`, finishes the block, decodes descriptions, prints suffix types, iterates keys, and performs seeks. The randomized test sorts generated keys with `Compare`, encodes them, decodes an aligned block, scans all keys, verifies materialized keys compare equal and are not longer than originals, seeks exact keys and prefixes, and checks stored values.

## State and Persistence Behavior
State is in-memory serialized columnar block data. The tests validate the bytes that would be persisted in SSTable data blocks, including schema-specific headers and decoded columns.

## Dependencies and Integration Points
Depends on `colblk`, `blockiter`, `binfmt`, `treeprinter`, `pebble.InternalKey`, `Comparer`, `KeySchema`, and parsing helpers from `cockroachkvs_test.go`.

## Risks and Edge Cases
Random engine keys are structurally valid enough for tests but may include arbitrary bytes. Synthetic suffix keys may materialize shorter normalized forms, so the test intentionally allows physical key differences while requiring logical equality. Datadriven expected output can require updates when encoding details change.

## Test Signals
Signals include exact block descriptions, suffix-type classification, ordered iteration, successful exact and prefix seeks, value equality, key validation, and preservation of logical equality across normalized materialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/key_schema_test.go -->
