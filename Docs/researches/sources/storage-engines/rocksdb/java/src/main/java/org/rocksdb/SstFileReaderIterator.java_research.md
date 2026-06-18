# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileReaderIterator.java

## Purpose
`SstFileReaderIterator` is the iterator wrapper used by `SstFileReader` to traverse key/value entries in an opened SST file.

## Important APIs and Types
It extends `AbstractRocksIterator<SstFileReader>`. Public APIs add `key()`, `key(ByteBuffer)`, `value()`, and `value(ByteBuffer)` while inherited iterator movement/status APIs are implemented through native overrides such as `seekToFirst0`, `seek0`, `next0`, `prev0`, `refresh0`, and `status0`.

## Control Flow
The constructor binds a native iterator handle to the owning reader. Movement methods are inherited and routed to JNI. Array-returning key/value calls allocate Java byte arrays from native slices. Buffer overloads choose direct-buffer JNI paths when `ByteBuffer.isDirect()` is true and array-backed paths otherwise, then adjust the buffer limit to expose the bytes actually copied.

## State and Persistence Behavior
The iterator owns a native iterator handle and is valid only while the associated native resources remain live. It does not persist state; current position is native state. Returned array data is copied, while buffer overloads write into caller-provided buffers.

## Dependencies and Integration Points
It depends on `AbstractRocksIterator`, `SstFileReader`, `ByteBuffer`, and the native SST iterator implementation. It is created only by `SstFileReader.newIterator`.

## Risks and Test Signals
Tests should exercise direct and heap `ByteBuffer` reads, too-small buffers and returned required sizes, seeking and reverse iteration, `status()` error propagation, and behavior after close. A notable risk is heap buffer handling assumes accessible backing arrays; read-only or non-array heap buffers would fail at runtime.
