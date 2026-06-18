# sources/storage-engines/rocksdb/db/db_clip_test.cc

## Purpose
`db_clip_test.cc` is a focused RocksDB regression test for `DB::ClipColumnFamily()`. It verifies that clipping a column family to a user-key half-open range removes all keys outside the range, preserves keys inside the range, and rewrites/retains live table metadata so every remaining file is fully contained by the clipped bounds. The scenario covers both a simple L0-only layout and a mixed-level layout after explicit compaction and new overlapping flushes.

## Important APIs, Types, And Functions
The file defines `DBClipTest`, a `DBTestBase` fixture using the database name `db_clip_test` and `env_do_fsync=true`. The only test case, `TestClipRange`, uses `Options`, `Random`, `Put`, `Flush`, `FilesPerLevel`, `ClipColumnFamily`, `Get`, `GetLiveFilesMetaData`, `CompactRange`, and the internal test helper `TEST_CompactRange`.

The key API under test is `db_->ClipColumnFamily(db_->DefaultColumnFamily(), begin_key, end_key)`. The test asserts the clipped range semantics with `ReadOptions` and direct `Get` calls, then validates physical file bounds using `LiveFileMetaData::smallestkey` and `LiveFileMetaData::largestkey`. It uses `Key(int)` from `DBTestBase`, which produces comparator-compatible encoded test keys.

## Control Flow
The test opens a DB with three levels, large write buffers, disabled automatic compaction, a level multiplier of two, and statistics enabled. It writes ten flushed L0 files covering logical ranges `[0, 100)`, `[100, 200)`, through `[900, 1000)`, storing the generated 10 KB values in a `std::map` for later verification.

The first clip keeps `[Key(251), Key(751))`. The test confirms keys `0..250` and `751..999` are not found, keys `251..750` return their original values, and all live files have smallest/largest keys within the clipped interval. It then performs a manual compact range with `change_level=true` and `target_level=2`, expecting the layout `"0,0,3"`.

The test next reintroduces even hundred-blocks into L0, compacts them to L1 with `TEST_CompactRange(0, ...)`, then reintroduces odd hundred-blocks into L0. With files now spread across L0, L1, and L2, it clips a wider `[Key(222), Key(888))` interval and repeats the logical and metadata checks.

## State And Persistence Behavior
The test models persistent table-file state rather than only point-lookups. `Flush()` creates physical SST files, `CompactRange()` moves and rewrites those files across levels, and `ClipColumnFamily()` must leave the column family in a state where out-of-range key versions are gone from reads and no live file metadata advertises a range outside the requested clip.

The two clip phases exercise different persistence shapes. The first phase starts with ten L0 files and expects clipping to prune/split/rewrite enough files that every live file is bounded by `251..750`. The second phase validates clipping after previously clipped data has been compacted to L2 and then overlapped with fresh L0/L1 data, so the API must handle file deletion and range trimming across levels.

## Dependencies And Integration Points
The fixture depends on `db/db_test_util.h` for `DBTestBase`, test key generation, reopen/destroy helpers, level/file counting, and assertion helpers. It uses RocksDB public DB APIs for column family clipping, reads, manual compaction, and live file metadata, plus the internal `DBImpl` test compaction helper exposed through `dbfull()`.

Integration points include the configured comparator, file metadata reporting, manual compaction level placement, the LSM manifest state behind `FilesPerLevel`, and `ClipColumnFamily()` behavior on the default column family handle.

## Risks
The main correctness risk is boundary handling. The expected interval is half-open: `begin_key` is retained and `end_key` is excluded. A comparator mismatch or use of raw `std::string::compare` on a non-bytewise comparator could make metadata validation misleading; the first check uses `options.comparator`, while the second uses string comparison because the test keys are byte-comparable.

Another risk is assuming file ranges align with the inserted hundred-key blocks. Compaction can merge or split files according to target file size and level state, so the test correctly verifies both logical reads and live metadata rather than relying only on expected file counts after clipping. The assertions are sensitive to changes in compaction output sizing and level placement.

## Test Signals
Passing signals include exact file counts before/after explicit compactions (`"10"`, `"0,0,3"`, `"5,0,3"`, `"0,5,3"`, `"5,5,3"`), not-found status outside clipped ranges, exact value preservation inside clipped ranges, and metadata bounds fully contained in the clip interval after each call to `ClipColumnFamily()`.

Failure signals would point to inclusive/exclusive boundary bugs, failure to remove out-of-range table data, failure to preserve in-range values through clipping, or stale live-file metadata/manifest entries after clipping a mixed-level LSM.
