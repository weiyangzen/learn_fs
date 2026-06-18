# sources/storage-engines/rocksdb/db/repair_test.cc

## Purpose

`repair_test.cc` is the DB-level regression suite for `RepairDB`. It verifies repair after missing/corrupt manifests, missing/corrupt SSTs, unflushed WAL-only data, timestamped keys, separate WAL directories, multiple column families, column-family-specific options, and DB paths with trailing slashes.

## Important APIs, Types, and Helpers

`RepairTest` derives from `DBTestBase` and adds `GetFirstSstPath` plus `ReopenWithSstIdVerify`, which uses `SyncPoint` to assert unique SST IDs in the repaired manifest can be verified. `RepairTestWithTimestamp` derives from timestamp test utilities and parameterizes paranoid file checks and user-defined timestamp persistence mode. Tests call `RepairDB` overloads, DB open/reopen helpers, `Put`, `Flush`, `DeleteRange`, `GetLiveFiles`, `GetSortedWalFiles`, `GetAllDataFiles`, `GetPropertiesOfAllTables`, and CF open/create/drop helpers.

## Control Flow and State Behavior

Manifest tests delete, corrupt, or replace the manifest and expect repair to rebuild a DB containing surviving SST data. `LostManifestMoreDbFeatures` includes an SST containing only a range tombstone and verifies deleted keys remain hidden after repair. `SortRepairedDBL0ByEpochNumber` checks recovered L0 files are ordered so the newest value wins.

SST damage tests delete or overwrite one SST while preserving metadata, then assert repair keeps exactly one of two key/value pairs. `UnflushedSst` deletes the manifest while data exists only in the WAL and expects repair to convert the WAL into an SST and remove WAL files. The timestamp parameterized test verifies WAL-to-SST repair with timestamped keys, persisted or stripped timestamps, paranoid checks, and correct repaired file boundaries.

`SeparateWalDir` repeats WAL repair across WAL option variants. `RepairMultipleColumnFamilies` verifies SSTs and WAL entries remain associated with original CFs. `RepairColumnFamilyOptions` verifies known and unknown CF option paths preserve comparators, including reverse bytewise comparator table properties. `DbNameContainsTrailingSlash` checks path normalization support.

## Persistence, Dependencies, and Integration

The suite manipulates real DB files under the test environment: deleting manifests, corrupting SSTs, copying descriptor files, and inspecting table/WAL files. It integrates repair with unique SST ID verification, timestamp comparators, WAL option matrix, table properties, column-family descriptors, and file utilities.

## Risks and Test Signals

Strong signals include successful reopen after repair with `verify_sst_unique_id_in_manifest`, expected key visibility, zero WALs after WAL conversion, nonzero SST size after repair, correct timestamp/file-boundary behavior, and comparator names in repaired CF tables. Residual risk remains around complex corruption patterns, blob files, custom merge operators, and time-consistent recovery, which repair explicitly does not guarantee.
