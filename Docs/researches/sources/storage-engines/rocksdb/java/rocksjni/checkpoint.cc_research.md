<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/checkpoint.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/checkpoint.cc

## Purpose
Exposes `org.rocksdb.Checkpoint` creation, destruction, checkpoint directory creation, and column-family export. Important entry points are `newCheckpoint`, `disposeInternalJni`, `createCheckpoint`, and `exportColumnFamily`.

## Important APIs and Types
Checkpoint Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`newCheckpoint` casts a Java `long` DB handle to `rocksdb::DB*`, calls `Checkpoint::Create`, and returns the raw `Checkpoint*`. `createCheckpoint` converts a Java path with `GetStringUTFChars`, calls `CreateCheckpoint`, releases the string, then maps non-OK `Status` to `RocksDBExceptionJni`. `exportColumnFamily` also casts a `ColumnFamilyHandle*`, receives an allocated `ExportImportFilesMetaData*`, and returns its pointer to Java.

## State and Persistence Behavior
Native state is owned through Java handles. `Checkpoint*` is deleted here; exported metadata must be deleted by its own JNI wrapper. The checkpoint/export operations persist RocksDB files on the filesystem, but this file only forwards paths and errors.

## Dependencies and Integration Points
Depends on `rocksdb/utilities/checkpoint.h`, `rocksdb/db.h`, `portal.h`, and pointer conversion macros. Risks are unchecked `Checkpoint::Create` status, null DB/CF handles, and ensuring strings are always released. Tests should cover invalid paths, export disposal, and Java exception propagation.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/checkpoint.cc -->
