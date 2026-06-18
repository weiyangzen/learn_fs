# sources/sync-backup/kopia/internal/epoch/epoch_range.go

Purpose: represents range checkpoint metadata and selects the best contiguous checkpoint chain starting at epoch 0.

Important APIs/types/functions: `RangeMetadata`, `findLongestRangeCheckpoint`, and recursive memoized `findLongestRangeCheckpointStartingAt`.

Control flow: groups range metadata by `MinEpoch`, then recursively tries checkpoints starting at the requested epoch, chaining to `MaxEpoch+1`. It chooses the chain whose final max epoch is greatest; ties prefer fewer checkpoint segments.

State and persistence behavior: no persistence here. `RangeMetadata.Blobs` references blob metadata for compacted checkpoint sets loaded by the manager.

Dependencies/integration: used during manager refresh after complete range compaction sets are discovered.

Risks/test signals: assumes valid non-overlapping semantics are enforced by selection rather than input validation. Empty input returns nil. Tests cover gaps, overlapping ranges, duplicate starts, and tie-breaking toward shorter chains.
