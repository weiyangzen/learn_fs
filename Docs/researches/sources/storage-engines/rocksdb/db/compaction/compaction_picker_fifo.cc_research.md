# sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.cc

## Purpose
This file implements `FIFOCompactionPicker`, the compaction picker for FIFO-style column families. FIFO compaction primarily deletes old files instead of merging levels, but this implementation also supports TTL-based deletion, size/capacity deletion, multi-level migration cleanup, file-temperature changes, and optional intra-L0 compaction to reduce file count. Local behavior includes blob-aware capacity accounting through `max_data_files_size` and a ratio-based intra-L0 compaction strategy for BlobDB-like workloads.

## Important APIs, Types, and Functions
Local helpers are `GetTotalFilesSize`, `GetEffectiveSizeAndLimit`, and `GetEffectiveMax`. Public overrides are `NeedsCompaction`, `PickCompaction`, and `PickCompactionForCompactRange`. Private pickers are `PickTTLCompaction`, `PickSizeCompaction`, `PickTemperatureChangeCompaction`, `PickIntraL0Compaction`, and `PickRatioBasedIntraL0Compaction`.

`NeedsCompaction` uses level-0 compaction score. `PickCompaction` tries TTL deletion first, then size deletion, intra-L0 file reduction, and temperature-change compaction. It registers the selected compaction, if any. FIFO manual compact-range delegates to the same automatic picking flow and only supports input/output level 0.

## Control Flow
`PickTTLCompaction` scans L0 from oldest to newest, using table properties and `FileMetaData::TryGetNewestKeyTime` to find files whose estimated newest key time is older than `ttl`. It computes remaining effective size. In blob-aware mode it estimates remaining total data as remaining SST across all levels plus a proportional share of blob bytes, then only picks TTL deletion when expired files exist and the remaining effective data is within the configured effective maximum.

`PickSizeCompaction` computes total SST size across all levels and combines it with blob size when `max_data_files_size` is configured. For regular L0 FIFO it drops oldest L0 files until remaining effective size is below the limit, using proportional data-per-file accounting in blob-aware mode. During migration from level/universal to FIFO, it picks from the last non-empty non-L0 level, deleting leftmost files under the assumption that smaller keys often represent older data.

`PickIntraL0Compaction` is enabled by `compaction_options_fifo.allow_compaction`. It dispatches to ratio-based compaction when `use_kv_ratio_compaction` is valid with `max_data_files_size >= max_table_files_size`; otherwise it falls back to cost-based intra-L0 compaction. The fallback uses `PickCostBasedIntraL0Compaction` with `level0_file_num_compaction_trigger`, a max average bytes per deleted file based on write buffer size, and `max_compaction_bytes`.

`PickRatioBasedIntraL0Compaction` skips while non-L0 levels remain, rejects concurrent L0 compaction, requires trigger greater than one, computes a target compacted SST size from user `max_compaction_bytes` or from `max_data_files_size * sst_ratio / trigger`, builds geometric tier boundaries down to 10 KB, and picks contiguous oldest L0 batches smaller than a boundary whose accumulated bytes reach that boundary. The output file size limit is the selected boundary.

`PickTemperatureChangeCompaction` only applies to single-level FIFO. It scans oldest files by age thresholds, chooses one file whose target temperature differs from current temperature, and creates a one-file compaction with `CompactionReason::kChangeTemperature`.

## State and Persistence Behavior
The picker itself persists nothing. It creates `Compaction` objects whose execution either deletes input files, rewrites selected L0 files, or changes file temperature. It reads durable metadata from `VersionStorageInfo`, file sizes, blob stats, table properties, newest key times, file creation times, file temperature, and current time. Output compactions use no compression for deletion-style FIFO paths and configured compression for intra-L0 or temperature-change rewrites.

## Dependencies and Integration Points
Dependencies include `CompactionPicker`, `VersionStorageInfo`, `CompactionOptionsFIFO`, `MutableCFOptions`, `MutableDBOptions`, `FileMetaData`, table readers/properties, blob stats, logging, statistics/status utilities, temperature options, and shared `PickCostBasedIntraL0Compaction`. It integrates with DB scheduling through compaction score and with manual compact range by asserting FIFO level constraints.

## Risks and Edge Cases
Blob-aware accounting is approximate and assumes proportional blob ownership by SST bytes; skewed blob references can over-delete or under-delete relative to true data size. TTL compaction depends on newest key time and creation time being available and meaningful. Multi-level FIFO migration deletion by key order is only an approximation of FIFO age order. Ratio-based intra-L0 compaction trades higher L0 file count for lower write amplification and depends on trigger, target, and tier-boundary math. Concurrent L0 compactions are intentionally avoided. Temperature-change compaction returns only one file at a time and does not apply to multi-level FIFO.

## Test Signals
Relevant tests should cover FIFO TTL deletion, max table/data size deletion, blob-aware capacity behavior, migration from non-FIFO levels, `allow_compaction` fallback, ratio-based tiering, invalid ratio-based configurations, file-temperature thresholds, and manual compact-range behavior. Logs emitted through `LogBuffer` are useful diagnostic signals for why a FIFO pick was skipped or selected.
