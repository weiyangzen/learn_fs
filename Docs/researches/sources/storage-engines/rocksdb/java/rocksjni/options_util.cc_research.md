# sources/storage-engines/rocksdb/java/rocksjni/options_util.cc

## Purpose
Implements the native side of `org.rocksdb.OptionsUtil`, bridging Java callers to RocksDB C++ options-file utilities. It loads DB and column-family options from the latest DB `OPTIONS-*` file or from an explicit options file, exposes latest-options-file discovery, and reconstructs supported table-format configuration for Java-side `ColumnFamilyOptions`.

## Important APIs, Types, And Functions
The helper `build_column_family_descriptor_list(JNIEnv*, jobject, std::vector<ColumnFamilyDescriptor>&)` converts C++ `ColumnFamilyDescriptor` objects into Java `ColumnFamilyDescriptor` instances and appends them to the caller-provided `java.util.List`.

The JNI exports are `Java_org_rocksdb_OptionsUtil_loadLatestOptions`, `Java_org_rocksdb_OptionsUtil_loadOptionsFromFile`, `Java_org_rocksdb_OptionsUtil_getLatestOptionsFileName`, and `Java_org_rocksdb_OptionsUtil_readTableFormatConfig`. They wrap C++ `LoadLatestOptions`, `LoadOptionsFromFile`, `GetLatestOptionsFileName`, and table factory option extraction.

Important JNI support types come from `rocksjni/portal.h`: `JniUtil::copyStdString`, `ListJni`, `ColumnFamilyDescriptorJni`, `BlockBasedTableOptionsJni`, `RocksDBExceptionJni`, and `IllegalArgumentExceptionJni`. Native handles are interpreted as `ConfigOptions*`, `DBOptions*`, `Env*`, and `ColumnFamilyOptions*`.

## Control Flow
`loadLatestOptions` copies the Java DB path into a `std::string`, reinterprets the config and DB option handles, calls `LoadLatestOptions`, and either throws a Java `RocksDBException` or appends the returned column-family descriptors to `jcfds`. `loadOptionsFromFile` follows the same flow using an explicit options-file path and `LoadOptionsFromFile`.

`build_column_family_descriptor_list` first resolves `List.add`. For each descriptor, it constructs the Java descriptor wrapper, checks for pending JNI exceptions, calls `List.add`, and stops immediately if construction, Java method invocation, or list insertion fails. It does not clear the target list before appending.

`getLatestOptionsFileName` copies the DB path, calls `GetLatestOptionsFileName` with the provided `Env*`, throws on non-OK status, and returns a new Java UTF string for the resulting file name. `readTableFormatConfig` validates the `ColumnFamilyOptions` handle, checks that a table factory exists, supports only `BlockBasedTable`, extracts `BlockBasedTableOptions`, and constructs the matching Java `BlockBasedTableConfig`.

## State And Persistence Behavior
This file does not create or mutate RocksDB database contents. It reads persisted options metadata from DB directories or options files and writes the parsed values into caller-owned `DBOptions` plus newly constructed Java `ColumnFamilyDescriptor` wrappers. The persistent state it depends on is the RocksDB `OPTIONS-*` file set and the filesystem view exposed through `Env`.

Native ownership remains with the Java wrapper pattern: the method receives raw native handles owned by Java `ConfigOptions`, `DBOptions`, `Env`, and `ColumnFamilyOptions` objects. The constructed Java column-family descriptors encapsulate copied native option state created by the portal helpers. Local JNI references are deleted only on early error paths; on successful list insertion the local references are left for normal JNI frame cleanup.

## Dependencies And Integration Points
The public Java companion `OptionsUtil.java` calls these natives, then runs `loadTableFormatConfig` over returned descriptors so each `ColumnFamilyOptions` receives the fetched Java `TableFormatConfig`. `OptionsUtilTest.java` exercises loading latest options, loading from file, block-based table format restoration, and latest filename discovery.

The file integrates with RocksDB utility parsing (`rocksdb/utilities/options_util.h`), DB option structures (`rocksdb/db.h`), environment abstraction (`rocksdb/env.h`), and the Java binding conversion layer. The table-format branch is coupled to `TableFactory::kBlockBasedTableName()` and `BlockBasedTableOptionsJni::construct`.

## Risks And Edge Cases
There are no null-handle checks for `ConfigOptions*`, `DBOptions*`, `Env*`, or the Java list in the load and filename methods, so the Java layer must pass valid live objects. `readTableFormatConfig` does validate the column-family options handle and table factory, but unsupported table factories throw `IllegalArgumentException`.

The list builder appends to the supplied list and can leave a partially populated list if a later descriptor conversion or `List.add` fails. `CallBooleanMethod` returning false is treated as failure but no explicit Java exception is thrown in that case. `NewStringUTF` failure is not checked after successful filename lookup, so an allocation failure relies on the JVM's pending exception behavior. The table-format support is intentionally narrow: non-block-based table factories and pointer-valued table options are not reconstructed here.

## Test Signals
Direct Java coverage is in `OptionsUtilTest`. The main signals are restored DB option values, restored column-family names and options, successful reconstruction of `BlockBasedTableConfig` fields, and filenames beginning with `OPTIONS-`. Useful regression tests should also cover unsupported table factories, null/invalid handles where Java can expose them, pre-populated descriptor lists, and JNI exception paths during descriptor construction or list insertion.
