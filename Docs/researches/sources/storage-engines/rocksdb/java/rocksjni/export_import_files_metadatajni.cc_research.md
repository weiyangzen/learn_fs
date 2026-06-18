<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/export_import_files_metadatajni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/export_import_files_metadatajni.cc

## Purpose
Contains the disposer for metadata returned by checkpoint column-family export.

## Important APIs and Types
ExportImportFilesMetaData disposal bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`ExportImportFilesMetaData.disposeInternal` casts the opaque handle to `ExportImportFilesMetaData*` and deletes it.

## State and Persistence Behavior
The metadata describes exported SST files for later import. This file only manages the in-memory metadata object; exported files remain on disk.

## Dependencies and Integration Points
Depends on `rocksdb/utilities/checkpoint.h`. Risk is double-free or leak if Java import/export APIs disagree on ownership. Tests should export a column family, inspect/use metadata, then dispose exactly once.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/export_import_files_metadatajni.cc -->
