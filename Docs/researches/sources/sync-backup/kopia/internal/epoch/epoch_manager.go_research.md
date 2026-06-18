# sources/sync-backup/kopia/internal/epoch/epoch_manager.go

Purpose: manages Kopia repository index epochs, including current write epoch discovery, index writes, compaction selection, range checkpoints, deletion watermarks, and cleanup of superseded markers/indexes.

Important APIs/types/functions: `Parameters`, `DefaultParameters`, `CurrentSnapshot`, `Manager`, `NewManager`, `Current`, `Refresh`, `WriteIndex`, `GetCompleteIndexSet`, `MaybeAdvanceWriteEpoch`, `MaybeCompactSingleEpoch`, `MaybeGenerateRangeCheckpoint`, `CleanupMarkers`, `CleanupSupersededIndexes`, `AdvanceDeletionWatermark`, and blob prefix helpers.

Control flow: refresh loads epoch markers, deletion watermarks, single-epoch compactions, and range checkpoints concurrently, then loads nearby uncompacted epochs and sets `ValidUntil`. Writes choose the current uncompacted prefix and retry/cleanup if the snapshot expires or the epoch changes mid-write. Complete index set assembly starts from longest range checkpoints and fills remaining epochs from single compactions or uncompacted blobs. Maintenance compacts settled epochs, generates range checkpoints when enough settled epochs accumulate, advances epoch markers, and deletes superseded data only after safety margins.

State and persistence behavior: persistent protocol is encoded in blob names under prefixes `xe`, `xn`, `xs`, `xr`, and `xw`. In-memory state is `lastKnownState` guarded by mutex plus slow-operation counters and background wait group.

Dependencies/integration: uses blob storage/list/delete, `completeset`, `contentlog`, `maintenancestats`, `errgroup`, fake/injected time, and compactor callbacks.

Risks/test signals: correctness depends on storage clocks, complete-set naming, snapshot validity windows, and cleanup safety margins. Tests stress sequential/parallel writes, slow refresh/write retries, read-only refresh, compaction failures, range checkpointing, watermark behavior, parameter validation, and cleanup.
