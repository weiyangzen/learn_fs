# sources/sync-backup/kopia/internal/epoch/epoch_utils.go

Purpose: provides parsing, grouping, compacted-range, and oldest-uncompacted-epoch helpers for epoch manager state.

Important APIs/types/functions: `epochNumberFromBlobID`, `epochRangeFromBlobID`, `groupByEpochNumber`, `groupByEpochRanges`, `deletionWatermarkFromBlobID`, `closedIntRange`, `getRangeCompactedRange`, `oldestUncompactedEpoch`, `filterLowerThan`, and `getOldestUncompactedAfterEpoch`.

Control flow: blob ID parsers strip prefix text before first digit and parse epoch numbers separated by underscores. Grouping functions collect metadata by parsed single epoch or range. `oldestUncompactedEpoch` starts after the longest range checkpoint, verifies range compaction begins at epoch 0, then skips contiguous single-epoch compactions using sorted filtered keys.

State and persistence behavior: stateless helpers over `CurrentSnapshot` and blob metadata. They interpret persistent state encoded in blob IDs and watermark names.

Dependencies/integration: used by refresh, cleanup, and compaction selection logic.

Risks/test signals: parsers are permissive about prefixes and can ignore malformed IDs silently. Invalid range compaction not starting at epoch 0 returns `errInvalidCompactedRange`. Direct tests are represented through manager and range tests; parser-specific edge coverage is limited.
