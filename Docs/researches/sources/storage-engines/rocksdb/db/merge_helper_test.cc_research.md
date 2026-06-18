# sources/storage-engines/rocksdb/db/merge_helper_test.cc

## Purpose
`merge_helper_test.cc` validates `MergeHelper::MergeUntil` in controlled iterator scenarios. It uses an in-memory `VectorIterator` over synthetic internal keys to test operand accumulation, full merge, partial merge, snapshot boundaries, compaction filter interactions, corrupt keys, deletion bases, and oversized partial merge result rejection.

## Important APIs, types, and functions
`MergeHelperTest` owns an environment, internal key comparator, vector iterator, merge operator, optional `MergeHelper`, key/value vectors, and optional `test::FilterNumber`. `Run` constructs a `VectorIterator`, creates `MergeHelper`, seeks to first, and invokes `MergeUntil`. `AddKeyVal` appends encoded internal keys and values, with optional corruption of the key type.

Test cases include `MergeAtBottomSuccess`, `MergeValue`, `SnapshotBeforeValue`, `NoPartialMerge`, `SingleOperand`, `MergeDeletion`, `CorruptKey`, `FilterMergeOperands`, `FilterAllMergeOperands`, `FilterFirstMergeOperand`, `DontFilterMergeOperandsBeforeSnapshotTest`, and `LargePartialMergeResultRejected`.

## Control flow
The tests build ordered internal-key streams by hand. Bottom-level tests set `at_bottom=true` and a next user key to prove the helper can full-merge merge-only histories into a `kTypeValue`. Base-value and deletion tests confirm the helper merges queued operands with put/delete records and advances the iterator to the first non-consumed key.

Snapshot tests set `stop_before` so the helper stops before older records and returns `MergeInProgress`, preserving operands rather than crossing snapshot visibility. Non-partial and single-operand tests verify the fallback output when a complete merge is impossible. The corrupt-key test confirms the helper stops before a corrupt record and outputs merge-in-progress data when strict assertion mode is disabled.

Filter tests install `FilterNumber` to remove selected merge operands. They verify mixed filtering changes the final sum, all-filtered operands produce no merge output and leave surviving put/delete records for the caller, filtering can remove leading operands and lower the output sequence number, and operands at or below `latest_snapshot` are not filtered.

The large partial merge test defines a concatenating operator, creates operands around the 4GB boundary, forces the partial-merge path with `at_bottom=false`, and asserts corruption above the block-builder limit while accepting exactly `uint32_t::max()` bytes.

## State and persistence behavior
The test is memory-only, but it directly models compaction output. It checks iterator position after merge, output keys and values in `MergeHelper`, and whether output is OK, merge-in-progress, or corruption. Those are the same signals compaction uses to decide which records to write to new SSTs.

## Dependencies and integration points
The test depends on `dbformat`, RocksDB comparator APIs, test harness/utilities, fixed-width coding helpers, `VectorIterator`, and built-in merge operators. It intentionally bypasses DB and file layers to isolate merge helper decisions.

## Risks and edge cases
Because inputs are synthetic, the test must maintain correct internal-key order to represent real iterator streams. It does not cover blob or wide-column base values, timestamp GC lower bounds, shutdown, or `RemoveAndSkipUntil`; those need separate integration coverage. Big-memory tests are skipped without sufficient memory.

## Test signals
Passing this file gives focused confidence in merge compaction semantics: snapshot isolation, operand order, compaction-filter application, partial merge fallback, deletion base handling, corrupt key stopping, and size-limit enforcement.
