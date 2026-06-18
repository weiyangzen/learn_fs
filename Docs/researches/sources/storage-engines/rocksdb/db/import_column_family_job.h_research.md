# sources/storage-engines/rocksdb/db/import_column_family_job.h

Declares `ImportColumnFamilyJob`, the job object used to import one or more exported SST file sets into a new column family. It carries immutable DB/import options, source metadata, filesystem access, generated ingested-file metadata, and the `VersionEdit` to apply after preparation.

`ColumnFamilyIngestFileInfo` records smallest/largest internal keys for one imported CF group so cross-CF range overlap can be checked. The constructor stores `VersionSet`, target `ColumnFamilyData`, DB/env options, `ImportColumnFamilyOptions`, grouped `LiveFileMetaData*`, and `IOTracer`. `Prepare()` copies or links files into the DB and fills `files_to_import_`. `Run()` prepares `edit_`. `Cleanup()` compensates after success or failure. `edit()` and `files_to_import()` expose prepared state.

The lifecycle is `Prepare()` before manifest application, `Run()` under DB write exclusion, and `Cleanup()` with the final status. Members include `clock_`, `versions_`, `cfd_`, option references, `FileSystemPtr`, grouped imported files, `VersionEdit edit_`, metadata groups, and tracer.

Dependencies include column-family internals, external SST ingestion types, snapshots, DB/import public options, metadata, SST file writer metadata conventions, `VersionEdit`, and env options. It is called from column-family creation with import metadata.

Risks: physical file preparation and edit application are separate, so callers must call cleanup correctly; referenced options/metadata must outlive the job; exposed mutable `VersionEdit*` assumes single-owner application; grouped metadata and ingested-file vectors must stay index-aligned. Tests exercise it indirectly through `DB::CreateColumnFamilyWithImport()`.
