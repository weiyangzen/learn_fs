<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileIterator.cpp -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileIterator.cpp

## Purpose

JNI implementation for RawIterator operations used by ManagedRawSSTFileIterator: validity, advance, key/value copy, sequence number, record type, and close.

## Important APIs, types, and functions

Exports JNI functions `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_hasNext`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_next`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getKey`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getValue`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getSequenceNumber`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_getType`, `Java_org_apache_hadoop_hdds_utils_db_ManagedRawSSTFileIterator_closeInternal`. Uses RocksDB raw SST/iterator classes and the pointer conversion helper.

## Control flow

Each JNI method casts the jlong handle to RawIterator. Key/value methods copy RocksDB Slice data into a Java direct ByteBuffer through copyToDirect and return the full source length. closeInternal deletes the iterator.

## State and persistence behavior

Native state consists of heap-allocated RocksDB C++ reader/iterator objects whose addresses are returned to Java as `long` handles. Java close methods must call the matching delete function to release native memory.

## Dependencies and integration points

Depends on generated JNI headers, RocksDB `raw_sst_file_reader.h`, `raw_iterator.h`, `options.h`, and Java classes in `org.apache.hadoop.hdds.utils.db`.

## Risks and edge cases

GetDirectBufferAddress must return non-null and capacity must cover offset plus requested length; otherwise an IllegalArgumentException is thrown. Java use after close can dereference a freed iterator.

## Test signals

Native-profile integration tests should open real SST files, iterate with and without bounds, read large keys/values, verify sequence/type metadata, and stress close/error paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/native/ManagedRawSSTFileIterator.cpp -->
