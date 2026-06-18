# sources/sync-backup/kopia/internal/epoch/epoch_utils_test.go

Purpose: exercises epoch utility behavior used by Kopia repository epoch compaction and checkpoint bookkeeping. The tests cover parsing epoch numbers from blob IDs, grouping blob metadata by epoch number, integer sentinel constants, oldest-uncompacted epoch selection, and helper iterator transforms.

Important APIs/types/functions: `epochNumberFromBlobID`, `groupByEpochNumber`, `oldestUncompactedEpoch`, `getOldestUncompactedAfterEpoch`, `filterLowerThan`, `CurrentSnapshot`, `RangeMetadata`, `blob.Metadata`, `compactedEpochBlobPrefix`, and `rangeCheckpointBlobPrefix`. Local helpers synthesize single-epoch compaction sets and longest compacted ranges.

Control flow: table-driven tests feed representative blob IDs and snapshot states into unexported package functions. `TestOldestUncompactedEpoch` is the main behavioral matrix, mixing contiguous and non-contiguous single-epoch compaction sets with range checkpoint metadata and asserting either the next uncompacted epoch or `errInvalidCompactedRange`.

State/persistence behavior: no durable repository state is written, but the metadata shapes mirror persisted compaction and checkpoint blobs. The compatibility signal is important: non-contiguous single-epoch sets are intentionally accepted for older clients, while invalid compacted ranges are rejected.

Dependencies/integration: integrates with `repo/blob` metadata and epoch package internals. It also protects assumptions shared by epoch manager code that consumes compacted epoch sets and range checkpoint sets.

Risks/test signals: broad table coverage catches off-by-one errors around range ends, threshold filtering, and unsorted epoch input. The tests depend on access to unexported package functions and will need updates when epoch blob naming or compaction metadata semantics change.
