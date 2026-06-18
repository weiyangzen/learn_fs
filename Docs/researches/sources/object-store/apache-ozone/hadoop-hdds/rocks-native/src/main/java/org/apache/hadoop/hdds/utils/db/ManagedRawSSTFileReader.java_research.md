<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileReader.java

## Purpose

Java JNI facade for RocksDB RawSstFileReader, allowing Ozone to iterate raw SST entries including tombstones through the native ozone_rocksdb_tools library.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db`. Main type: `ManagedRawSSTFileReader`. Notable methods: `tryLoadLibrary`, `loadLibrary`, `newIterator`, `newRawSSTFileReader`, `newIterator`, `disposeInternal`, `close`. Key imports include `static org.apache.hadoop.hdds.utils.NativeConstants.ROCKS_TOOLS_NATIVE_LIBRARY_NAME`, `java.io.Closeable`, `java.util.Arrays`, `java.util.function.Function`, `org.apache.hadoop.hdds.utils.NativeLibraryLoader`, `org.apache.hadoop.hdds.utils.NativeLibraryNotLoadedException`, `org.apache.hadoop.hdds.utils.db.managed.ManagedOptions`, `org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils`, `org.apache.hadoop.hdds.utils.db.managed.ManagedSlice`, `org.slf4j.Logger`.

## Control flow

`loadLibrary` loads rocksdbjni and ozone_rocksdb_tools with the RocksDB JNI library as a dependent file. The constructor creates a native reader from ManagedOptions, file path, and read-ahead size. `newIterator` passes optional lower/upper ManagedSlice handles to native code and wraps the native iterator.

## State and persistence behavior

Holds fileName and a native RawSstFileReader pointer. close deletes the native reader.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

The constructor assumes the native library is already loaded. Slice handles must outlive iterator creation. Native handle double-close and missing close can crash or leak.

## Test signals

Use real SST fixtures under the native profile to read full and bounded ranges, verify tombstone visibility, and ensure close is idempotent or guarded by callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileReader.java -->
