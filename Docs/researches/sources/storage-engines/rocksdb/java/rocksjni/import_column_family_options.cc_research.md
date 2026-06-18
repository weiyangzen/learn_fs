<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/import_column_family_options.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/import_column_family_options.cc

## Purpose
Wraps `rocksdb::ImportColumnFamilyOptions`, currently exposing `move_files`.

## Important APIs and Types
ImportColumnFamilyOptions Java bridge. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
JNI methods allocate/delete the struct and set/get the `move_files` boolean controlling whether imported files are moved or copied.

## State and Persistence Behavior
Options are transient but directly affect filesystem persistence during column-family import: move can transfer ownership of files, while copy leaves source files intact.

## Dependencies and Integration Points
Depends on import-column-family utility API. Risks include data loss expectations around move semantics and use after dispose. Tests should import with move true/false and verify source/destination file existence.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/import_column_family_options.cc -->
