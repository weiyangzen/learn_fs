# sources/storage-engines/rocksdb/db/compaction/compaction_picker_fifo.h

## Purpose
This header declares `FIFOCompactionPicker`, the concrete `CompactionPicker` subclass for FIFO compaction style. It constrains compaction output to level 0 and exposes FIFO-specific picking paths for automatic and manual compaction.

## Important APIs, Types, and Functions
The public constructor accepts `ImmutableOptions` and an internal key comparator. Overrides are `PickCompaction`, `PickCompactionForCompactRange`, `MaxOutputLevel`, and `NeedsCompaction`. `MaxOutputLevel` always returns 0 because FIFO creates/deletes L0 files rather than cascading output into lower levels.

Private helpers declared here are `PickTTLCompaction`, `PickSizeCompaction`, `PickIntraL0Compaction`, `PickRatioBasedIntraL0Compaction`, and `PickTemperatureChangeCompaction`. The comments document that intra-L0 compaction is optional, ratio-based compaction is BlobDB-oriented, and the cost-based path is the original fallback.

## Control Flow
Callers use the standard picker interface. `PickCompaction` decides among FIFO policies and returns a registered `Compaction` or null. `PickCompactionForCompactRange` is FIFO-specific and ultimately reuses normal FIFO picking with level 0 assertions. The private method split makes policy order explicit in the implementation: expiration, capacity, file-count reduction, and temperature change.

## State and Persistence Behavior
The class introduces no new member state beyond `CompactionPicker`'s running compaction sets. It reads FIFO options and current version metadata during picking. Persistent effects are deferred to the returned `Compaction`: files may be deleted, compacted within L0, or rewritten with a target temperature.

## Dependencies and Integration Points
The header depends on `compaction_picker.h` and therefore on the base picker contract, `Compaction`, `VersionStorageInfo`, `MutableCFOptions`, `MutableDBOptions`, `LogBuffer`, snapshot placeholders, and compact range options. It is selected when a column family uses `kCompactionStyleFIFO`.

## Risks and Edge Cases
Because FIFO only permits output level 0, callers that expect normal level progression must use another picker. The manual compact-range override ignores begin/end range semantics in favor of FIFO policy picking, so it is not a general range compactor. Ratio-based intra-L0 compaction is configuration-sensitive and should be validated carefully when `max_data_files_size`, `max_table_files_size`, and `level0_file_num_compaction_trigger` change.

## Test Signals
Header-level behavior is validated indirectly by FIFO picker tests and DB tests that instantiate FIFO column families. Important observable signals are `MaxOutputLevel() == 0`, no compaction when score is below threshold, and correct compaction reasons from the implementation paths.
