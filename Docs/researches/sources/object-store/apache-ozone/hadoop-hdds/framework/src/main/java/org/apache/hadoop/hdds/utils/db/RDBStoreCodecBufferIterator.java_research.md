# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreCodecBufferIterator.java

## Purpose

`RDBStoreCodecBufferIterator` is the `CodecBuffer`-based RocksDB iterator implementation used by `RDBTable` and `TypedTable` when both key and value codecs support direct buffers. It avoids byte-array materialization for iteration-heavy metadata paths and plugs into the shared `RDBStoreAbstractIterator` prefix/seek/remove framework. The complete 100-line source was read for this report.

## Important APIs, Types, and Functions

The package-private class extends `RDBStoreAbstractIterator<CodecBuffer>`. It owns two reusable `Buffer` helpers, one for keys and one for values, plus an `AtomicBoolean closed`. Key methods are `key()`, `getKeyValue()`, `seek0(CodecBuffer)`, `delete(CodecBuffer)`, `startsWithPrefix(CodecBuffer)`, and `close()`.

## Control Flow

Construction wires RocksDB iterator accessors based on `IteratorType`: keys are read when the caller asks for keys or when prefix matching requires them, values are read only for value-capable iterator types. The constructor immediately seeks to the first valid element. `getKeyValue()` returns null keys for value-only iteration and uses the reusable buffers to fetch RocksDB key/value bytes. Seeking delegates to `ManagedRocksIterator.seek(ByteBuffer)`, and removal deletes through the owning `RDBTable`.

## State and Persistence Behavior

The iterator does not persist state itself; it holds native RocksDB iterator state and direct buffers that must be released. `close()` is idempotent, closes the superclass iterator, releases the optional prefix buffer, and releases key/value buffers. A leaked iterator keeps the parent `RocksDatabase` acquire counter open.

## Dependencies and Integration Points

It depends on `CodecBuffer`, `CodecBuffer.Capacity`, `ManagedRocksIterator`, `RDBTable`, `IteratorType`, and Ratis `Preconditions`. It is selected by `TypedTable.newCodecBufferTableIterator` and raw `RDBTable.iterator(CodecBuffer, IteratorType)`.

## Risks and Edge Cases

Closed iterators fail through `assertOpen()`. Prefix matching must read keys even for value-only output. The caller must not retain returned `CodecBuffer` instances beyond the iterator lifecycle unless ownership is clear. Failure to close can block `RocksDatabase.close()` because managed iterators carry the DB acquire reference.

## Test Signals

Useful tests include prefix iteration with all `IteratorType` modes, seek/delete behavior with direct-buffer codecs, close idempotence, use-after-close assertions, and leak-sensitive DB close tests that ensure iterators release native references.
