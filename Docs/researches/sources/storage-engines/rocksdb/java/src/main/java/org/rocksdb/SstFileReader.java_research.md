# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReader.java

## Purpose
`SstFileReader` wraps the native RocksDB `SstFileReader` so Java code can open and inspect external SST files without opening them as a database.

## Important APIs and Types
The constructor takes `Options` and calls native `newSstFileReader`. Public methods are `open(String filePath)`, `newIterator(ReadOptions)`, `verifyChecksum()`, and `getTableProperties()`. It returns `SstFileReaderIterator` and `TableProperties`.

## Control Flow
Construction allocates the native reader. `open` binds the reader to an SST file path. `newIterator` asserts ownership, asks native code for an iterator handle, and wraps it with this reader as the owning parent. Checksum and property calls delegate directly to native code and throw `RocksDBException` on native failures.

## State and Persistence Behavior
The Java object owns a native reader handle and releases it through `disposeInternalJni`. The underlying SST file is read-only; this class does not mutate the file, except that failed reads/checksum verification expose native status.

## Dependencies and Integration Points
It extends `RocksObject`, uses `Options`, `ReadOptions`, `SstFileReaderIterator`, `TableProperties`, and `RocksDBException`, and depends on matching JNI implementations.

## Risks and Test Signals
Tests should cover opening valid/invalid SST paths, checksum failure propagation, iterator lifetime after reader close, and table-property parity with files written by `SstFileWriter`. The class comment appears copied from transaction iterators and mentions uncommitted transaction keys, which is misleading for an SST-file reader.
