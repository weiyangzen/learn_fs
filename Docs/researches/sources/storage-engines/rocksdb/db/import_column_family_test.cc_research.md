# sources/storage-engines/rocksdb/db/import_column_family_test.cc

Integration tests for `CreateColumnFamilyWithImport()` and `ImportColumnFamilyJob`. The suite creates SSTs via `SstFileWriter` or exported checkpoints, imports them into new column families or new DBs, and verifies read semantics, metadata bounds, move/copy cleanup behavior, negative validation, multi-CF merging, and epoch-number repair.

`ImportColumnFamilyTest` extends `DBTestBase`, manages external SST/export directories, imported CF handles, and export metadata pointers. `LiveFileMetaDataInit()` creates minimal metadata for manually written SSTs. Tests use `SstFileWriter`, `Checkpoint::ExportColumnFamily()`, `DB::CreateColumnFamilyWithImport()` overloads, `Flush()`, `CompactRange()`, snapshots, metadata inspection, and sync points.

Scenarios include simple import from known/unknown CF SSTs, staged overlapping files across levels with value precedence checks after flush and compaction, range tombstone bounds, export/import from another CF and another DB, snapshot reads with range tombstones, endpoint-overlapping level files, negative cases, multi-CF imports, multi-CF overlap rejection, and a compaction-race epoch reassignment test.

The tests validate that imported files are visible immediately, survive writes/flushes/compactions/reopen, preserve snapshot visibility with range tombstones, handle move/copy import modes, and reject invalid inputs such as existing CF names, empty file lists, same-level overlaps, comparator mismatch, missing files, and overlapping imported CF ranges.

Dependencies span public DB APIs, checkpoint export format, table metadata, column-family metadata, filesystem directories, snapshots, compaction scheduling, and import job internals. Risks/gaps: failures are end-to-end and can be hard to localize; UDT import is not covered; hardlink fallback is not forced across filesystems; corrupt property and unique-ID warning paths are lightly covered. Strong signals are expected values/errors, metadata largest-key checks, manifest unique-ID reopen, and successful compaction after epoch repair.
