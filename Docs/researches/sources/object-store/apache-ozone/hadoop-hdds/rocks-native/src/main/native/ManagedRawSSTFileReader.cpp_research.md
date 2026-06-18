<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileReader.cpp -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileReader.cpp

## Purpose

JNI implementation for creating/deleting RocksDB RawSstFileReader instances and creating bounded RawIterator instances from optional lower and upper Slice handles.

## Important APIs, types, and functions

Exports JNI functions `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileReader_newRawSSTFileReader`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileReader_newIterator`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileReader_disposeInternal`. Uses RocksDB raw SST/iterator classes and the pointer conversion helper.

## Control flow

newRawSSTFileReader casts the Java options handle, obtains the UTF-8 file path, constructs RawSstFileReader with read-ahead and checksum options, releases the Java string, and returns the pointer handle. newIterator casts optional slice handles and calls raw_sst_file_reader->newIterator. disposeInternal deletes the reader.

## State and persistence behavior

Native state consists of heap-allocated RocksDB C++ reader/iterator objects whose addresses are returned to Java as `long` handles. Java close methods must call the matching delete function to release native memory.

## Dependencies and integration points

Depends on generated JNI headers, RocksDB `raw_sst_file_reader.h`, `raw_iterator.h`, `options.h`, and Java classes in `org.apache.hadoop.hdds.utils.db`.

## Risks and edge cases

If RawSstFileReader construction throws or env string acquisition fails, the current code has no Java exception translation. It assumes slice handles are valid and owned elsewhere.

## Test signals

Native-profile integration tests should open real SST files, iterate with and without bounds, read large keys/values, verify sequence/type metadata, and stress close/error paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileReader.cpp -->
