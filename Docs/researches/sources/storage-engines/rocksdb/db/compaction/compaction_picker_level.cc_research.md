# sources/storage-engines/rocksdb/db/compaction/compaction_picker_level.cc

## Purpose
Implements RocksDB's leveled-compaction picker. The file decides whether a column-family version has compaction work, chooses input files for ordinary leveled compactions, special marked-file compactions, TTL/periodic/read-triggered/blob-GC compactions, trivial moves, and intra-L0 compactions, then constructs and registers a `Compaction` object for execution by the compaction subsystem.

The implementation is deliberately policy-heavy: it does not compact data itself, but turns `VersionStorageInfo` state plus immutable/mutable options into a concrete compaction plan while preserving clean-cut user-key boundaries and avoiding overlap with running compactions.

## Important APIs, Types, And Functions
- `LevelCompactionPicker::NeedsCompaction(const VersionStorageInfo*)`: fast readiness check. It returns true for expired TTL files, periodic files, bottommost tombstone-cleanup files, files explicitly marked for compaction, forced blob-GC files, read-triggered files, or any compaction score at least one up to `MaxInputLevel()`.
- `LevelCompactionPicker::PickCompaction(...)`: public override from `CompactionPicker`. It instantiates the anonymous `LevelCompactionBuilder` and delegates all selection work to `builder.PickCompaction()`. The snapshot-related parameters and `require_max_output_level` are unused by this picker.
- `CompactToNextLevel`: local enum controlling special marked-file routing: keep in the same level (`kNo`), move to next/base level (`kYes`), or move to next/base except when the candidate is already in the last non-empty level (`kSkipLastLevel`).
- `LevelCompactionBuilder`: local stateful builder that carries the currently selected start level, output level, input vectors, overlap parent/base indexes, grandparents, compaction reason, and option references while it incrementally builds one compaction.
- `SetupInitialFiles()`: priority ladder for choosing the first candidate. It first tries score-based compactions, including L0 fallback to intra-L0 work when L0-to-base is blocked. If no score candidate works, it tries explicit marked files, bottommost files, TTL, periodic, forced blob GC, and read-triggered candidates in that order.
- `PickFileToCompact()` overloads: one overload picks from special `(level, file)` vectors; the no-argument overload picks a score-priority file from `VersionStorageInfo::FilesByCompactionPri()`, expands to a clean cut, checks running-compaction overlaps, handles trivial moves, and updates the next compaction index for non-round-robin priorities.
- `TryPickL0TrivialMove()` and `TryExtendNonL0TrivialMove()`: recognize file sets that can be moved to the output level without rewriting, guarded by compression and multi-path constraints.
- `PickIntraL0Compaction()` and `PickSizeBasedIntraL0Compaction()`: choose L0-to-L0 work to reduce L0 pressure or avoid inefficient L0-to-base write amplification.
- `SetupOtherL0FilesIfNeeded()` and `SetupOtherInputsIfNeeded()`: after a start-level candidate is selected, these add overlapping L0/output-level files, optionally expand round-robin non-L0 inputs, fetch grandparents, and reject output ranges that overlap running compactions.
- `SetupOtherFilesWithRoundRobinExpansion()`: round-robin-only expansion for non-L0 level-size compactions. It tries to add consecutive files while respecting clean cuts, running compactions, `max_compaction_bytes`, and the amount needed to bring the level back under target size.
- `GetCompaction()`: creates the `Compaction`, registers it with the shared picker, and recomputes compaction scores because selected files become part of in-progress work.
- `GetPathId(...)`: static path selection helper that maps the output level to a configured CF path based on target sizes and level-size growth.

## Control Flow
The public `PickCompaction()` method is a thin wrapper. It builds a `LevelCompactionBuilder` with the column-family name, current `VersionStorageInfo`, base `CompactionPicker`, logging buffer, options, mutable DB options, and `full_history_ts_low`, then calls `LevelCompactionBuilder::PickCompaction()`.

`LevelCompactionBuilder::PickCompaction()` runs three phases. First, `SetupInitialFiles()` selects an initial candidate. It scans compaction scores in descending order from `VersionStorageInfo::CompactionScore()` and `CompactionScoreLevel()`. For L0 it targets the base level; for L1+ it targets the next level. If a score-based candidate is blocked, L0 has special fallback to intra-L0 compaction so L0 file count can still fall while L0-to-base is blocked. Once score work is exhausted, the builder tries explicit marked-file families: files marked for compaction, bottommost files, round-robin TTL, general TTL, periodic compaction, forced blob GC, and read-triggered compaction. Each successful branch sets a precise `CompactionReason`.

Second, the builder completes inputs. If the selected compaction starts in L0 and outputs below L0, `SetupOtherL0FilesIfNeeded()` pulls in overlapping L0 files through `CompactionPicker::GetOverlappingL0Files()`. `SetupOtherInputsIfNeeded()` then finds output-level overlaps through `CompactionPicker::SetupOtherInputs()`, unless the compaction is an L0 trivial move. For round-robin level-size compactions, it first calls `SetupOtherFilesWithRoundRobinExpansion()` to include additional consecutive start-level files when that can reduce level pressure without breaking clean-cut or byte-budget constraints.

Third, `GetCompaction()` materializes the plan. It computes whether L0 inputs might overlap, creates a `Compaction` with file-size, compression, path, reason, score, grandparents, and option metadata, registers the compaction so selected files are treated as in-progress, and immediately calls `VersionStorageInfo::ComputeCompactionScore()` to refresh score/order state after registration.

## State And Persistence Behavior
The file is mostly in-memory planner logic. It reads `VersionStorageInfo` file metadata, compaction scores, file-priority order, pending marked-file vectors, base level, non-empty level count, configured CF paths, and running compaction state exposed through `CompactionPicker`. It mutates builder-local input vectors while selecting candidates.

The externally visible state effects happen only after a `Compaction` is created: `CompactionPicker::RegisterCompaction(c)` marks/registers the selected compaction and prevents conflicting L0 or overlapping-range compactions from being scheduled concurrently; `VersionStorageInfo::ComputeCompactionScore()` refreshes in-memory compaction scores after those files become in-progress. The code also advances `VersionStorageInfo::SetNextCompactionIndex()` for non-round-robin score picking so future calls continue scanning from the chosen priority cursor.

No manifest edit, SST write, blob file change, or durable metadata write occurs in this file. Actual file rewrite/trivial-move execution and durable `VersionEdit`/MANIFEST persistence are owned downstream by compaction job/version-set code. Round-robin cursor persistence is tested elsewhere, but this file's round-robin path intentionally does not update the normal next-compaction index in `PickFileToCompact()`.

## Dependencies And Integration Points
- Depends on `db/compaction/compaction_picker_level.h` for the class declaration and `db/compaction/compaction_picker.h` for base helper methods such as `ExpandInputsToCleanCut()`, `SetupOtherInputs()`, `FilesRangeOverlapWithCompaction()`, `GetOverlappingL0Files()`, `GetGrandparents()`, and `RegisterCompaction()`.
- Depends heavily on `VersionStorageInfo` from the version-set layer for live file layout, scores, marked-file queues, level sizes, file priorities, base-level routing, and compaction-score recomputation.
- Integrates with `Compaction` construction: output level, max output file size, max compaction bytes, compression type/options, path ID, grandparents, compaction reason, score, and L0-overlap marker are passed into the `Compaction` object consumed by compaction execution.
- Uses option state from `ImmutableOptions`, `MutableCFOptions`, and `MutableDBOptions`, including `compaction_pri`, `level_compaction_dynamic_level_bytes`, compression-per-level settings, DB/CF path layout, `max_compaction_bytes`, `level0_file_num_compaction_trigger`, `max_bytes_for_level_base`, and `max_bytes_for_level_multiplier`.
- Uses `InternalKeyComparator` and its user comparator to maintain clean user-key cuts, especially when extending trivial moves across adjacent files with equal user-key boundaries.
- Uses shared helpers such as `PickCostBasedIntraL0Compaction()`, `MultiplyCheckOverflow()`, `MaxFileSizeForLevel()`, `GetCompressionType()`, and `GetCompressionOptions()`.
- `LevelCompactionPicker` is installed for leveled compaction column families in `db/column_family.cc`. Compaction job and output code interpret the `CompactionReason`, including round-robin TTL and round-robin output splitting behavior.
- `TEST_SYNC_POINT` hooks expose scheduling edges to unit/integration tests without changing production behavior.

## Risks And Edge Cases
- Clean-cut correctness is central. If `ExpandInputsToCleanCut()` or the extra boundary checks around trivial-move extension are bypassed incorrectly, compactions can split versions across the same user key and violate snapshot/key visibility invariants.
- Concurrency safety depends on repeated `being_compacted` and `FilesRangeOverlapWithCompaction()` checks. The file explicitly handles edge cases from non-exclusive manual compaction and file ingestion where overlapping output ranges could otherwise be scheduled concurrently.
- L0 logic has several special cases because L0 files overlap. Regular L0-to-base compaction is blocked by any existing L0 compaction, but intra-L0 compaction can still run when chosen as an independent span. A mistake here can either over-serialize L0 work or create unsafe parallel L0 interaction.
- Round-robin expansion is sensitive to cursor/index assumptions. It only expands forward through consecutive files, gives up when clean-cut expansion pulls locked files, and includes a TODO for future parallel round-robin cursor behavior. The code has a known regression-test area around shared user-key boundaries.
- Trivial move detection is intentionally conservative. It is disabled with compression-per-level and multiple DB paths because output compression/path placement can make a physical move unsafe or hard to predict.
- `GetPathId()` estimates level placement based on configured target sizes and has comments about dynamic level bytes being ignored for multiple DB paths elsewhere. Misconfiguration can still route output to the fallback path.
- Marked-file priority order matters operationally. Explicit compaction marks, bottommost tombstone cleanup, TTL, periodic compaction, forced blob GC, and read-triggered work only run after score-based work fails to choose a candidate, which can affect latency of maintenance compactions under sustained level pressure.
- The builder stores `log_buffer_` but this implementation does not emit log messages through it, so debugging relies on callers, tests, and sync points rather than local picker logs.

## Test Signals
Concrete local test coverage is visible in RocksDB compaction tests:
- `db/compaction/compaction_picker_test.cc` directly constructs `LevelCompactionPicker` and covers round-robin priorities, multiple-file round-robin selection, bottommost-file marking, range-overlap checks, and intra-L0 cost/selection paths.
- `db/db_compaction_test.cc` uses `LevelCompactionPicker::PickCompaction:Return`, `LevelCompactionPicker::PickCompactionBySize:0`, `PickCostBasedIntraL0Compaction`, and round-robin tests to verify blocked L0 behavior, TTL round-robin reasons, cursor persistence, subcompaction/resource behavior, and the regression around `SetupOtherFilesWithRoundRobinExpansion()` plus clean-cut shared boundaries.
- `db/column_family_test.cc`, `db/db_options_test.cc`, `util/compression_test.cc`, and `db/db_with_timestamp_compaction_test.cc` observe picker returns via sync points in broader DB flows.
- `db/version_set_test.cc` validates the version-storage side of forced blob-GC and marked-file queues that `NeedsCompaction()` and `SetupInitialFiles()` consume.

Useful manual or automated signals for future changes include: selected `CompactionReason`, input/output level vectors, whether `RegisterCompaction()` prevents a second overlapping pick, next-compaction-index movement for non-round-robin priorities, absence of same-user-key boundary splits after input expansion, and score recomputation after pick registration.
