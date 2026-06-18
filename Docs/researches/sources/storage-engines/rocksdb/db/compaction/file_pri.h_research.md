<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/file_pri.h -->
# sources/storage-engines/rocksdb/db/compaction/file_pri.h

## Purpose
This header defines `FileTtlBooster`, a helper that boosts compaction priority for files approaching TTL-based compaction thresholds. It avoids overloading `FileMetaData::compensated_file_size` for TTL urgency, because that size is broadly used as a file-size proxy.

## Important APIs, Types, and Functions
`FileTtlBooster` has a constructor taking current time, TTL, number of non-empty levels, and the candidate level. `GetBoostScore(FileMetaData*)` returns an integer multiplier-like score: `1` when disabled or not old enough, and a linearly increasing value after the level-specific boost start age. Private fields are `enabled_`, `current_time_`, `boost_age_start_`, and `boost_step_`.

## Control Flow
Boosting is disabled when TTL is zero, the level is L0, or the level is at/after the last non-empty level. Otherwise, the constructor starts boosting after half the TTL plus a level-dependent range, with lower levels starting later. The range shrinks by right-shifting according to distance from the last non-empty level, and `boost_step_` is guarded to at least one. `GetBoostScore` reads the file's oldest ancestor time, computes age if it is in the past, and returns `(age - boost_age_start_) / boost_step_ + 1` once the file is old enough.

## State and Persistence Behavior
The class is stateless beyond constructor-derived thresholds and does not persist anything. It reads `FileMetaData::TryGetOldestAncesterTime`, so its behavior reflects persisted or propagated file creation/ancestor timestamps.

## Dependencies and Integration Points
The header includes `<algorithm>` and `db/version_edit.h` for `FileMetaData`. It is intended for compaction priority calculations where file ordering can incorporate TTL urgency without changing file-size accounting.

## Risks and Edge Cases
The comments acknowledge the formula is intentionally simple and production-tunable. Shifting is capped at 63 to avoid undefined behavior for many levels. Very large or manipulated current times can overflow boost arithmetic, which the code explicitly ignores for simplicity. Misspellings in comments and the `TryGetOldestAncesterTime` API name are existing code style, not functional issues.

## Test Signals
Signals should come from compaction-priority tests that configure TTL compaction and inspect picked files by age/level. Important cases are TTL zero, L0, last level, files newer than boost start, and files very close to the TTL threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/file_pri.h -->
