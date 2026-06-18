# sources/storage-engines/rocksdb/db/import_column_family_job.cc

Implements `ImportColumnFamilyJob`, which imports existing SST files into a newly created column family without rewriting table contents. It validates metadata, copies or hardlinks external files into the DB, builds a `VersionEdit` that adds them at their original levels, repairs epoch numbers for multi-CF imports, and cleans up on failure or move-file success.

`Prepare(next_file_number, sv)` reads all `LiveFileMetaData`, calls `GetIngestedFileInfo()` for each file, rejects empty/corrupt files, computes each imported CF's key range, rejects overlapping CF ranges, and materializes files inside DB table paths. `Run()` builds dummy `VersionBuilder`/`VersionStorageInfo` per imported CF, adds files with original level/sequence metadata, recovers epoch numbers, populates `edit_`, and advances version last sequence if needed. `Cleanup(status)` deletes copied DB files on failure or original links after successful move import. `GetIngestedFileInfo()` opens table readers and derives size, bounds, properties, unique ID, and range-tombstone-aware smallest/largest keys.

Preparation happens before manifest application. Hardlinking is attempted when `move_files` is true and falls back to copy when unsupported. `Run()` requires exclusive writer/nonmem-writer ownership and simulates version construction so consistency checks and epoch recovery happen before adding files to the real edit.

State includes grouped `files_to_import_`, `edit_`, DB/options references, filesystem handle, source metadata groups, and IO tracer. Persistent effects are file additions in `edit_`, version sequence advancement, and physical file copies/links. Import time becomes oldest ancestor and creation time.

Dependencies include `VersionSet`, `ColumnFamilyData`, filesystem APIs, `CopyFile`, `TableReader`, table properties, range tombstone iterators, `VersionBuilder`, `VersionStorageInfo`, epoch recovery, and checkpoint/export metadata. Risks include cleanup after pre-manifest file materialization, subtle range tombstone bounds, UDT import TODO, PlainTable full scan for largest key, unique-ID warning paths, and duplicate epoch corruption if recovery is wrong.

`import_column_family_test.cc` covers writer SST imports, overlapping files/ranges, range tombstones, exports from another CF/DB, move/copy behavior, negative cases, multi-CF imports, endpoint overlaps, and epoch reassignment under compaction pressure.
