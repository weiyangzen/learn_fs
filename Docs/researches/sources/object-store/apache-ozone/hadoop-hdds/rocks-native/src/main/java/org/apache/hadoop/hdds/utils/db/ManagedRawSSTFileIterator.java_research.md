<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileIterator.java

## Purpose

Closable Java iterator over native RocksDB RawIterator records, transforming raw key/sequence/type/value tuples into caller-defined objects.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db`. Main type: `ManagedRawSSTFileIterator`. Notable methods: `hasNext`, `next`, `getKey`, `getValue`, `getSequenceNumber`, `getType`, `hasNext`, `next`, `closeInternal`, `close`, `getKey`, `getSequence`, `getType`, `getValue`, `toString`. Key imports include `com.google.common.primitives.UnsignedLong`, `java.nio.ByteBuffer`, `java.util.NoSuchElementException`, `java.util.function.Function`, `org.apache.hadoop.ozone.util.ClosableIterator`.

## Control flow

`next` checks native hasNext, pulls key/value into dynamically sized CodecBuffers according to IteratorType, reads unsigned sequence and type, advances the native iterator, and applies the transformer.

## State and persistence behavior

Owns a native iterator pointer, key/value buffers, transformer, IteratorType, and closed flag.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

hasNext does not check `closed`, so using after close can touch freed native memory. Buffer sizing depends on native copy methods returning full source lengths. Transformer owns returned CodecBuffers and must release if required.

## Test signals

Native integration tests should cover keys/values larger than initial buffers, key-only/value-only iterator types, close behavior, and NoSuchElementException.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocks-native/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedRawSSTFileIterator.java -->
