# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBStoreCodecBufferIterator.java

Purpose: Mirrors byte-array iterator tests for `RDBStoreCodecBufferIterator`, validating the direct `CodecBuffer` path that avoids unnecessary array copies.

Important APIs/types/functions: `RDBStoreCodecBufferIterator`, `CodecBuffer`, `ManagedRocksIterator`, `RDBTable.delete(ByteBuffer)`, `IteratorType.KEY_AND_VALUE`, `seek(ByteBuffer)`, `key(ByteBuffer)`, and `value(ByteBuffer)`.

Control flow: Helper answers write bytes into supplied `ByteBuffer` instances to emulate RocksDB direct-buffer APIs. Tests cover foreach iteration, `hasNext`, constructor and explicit seeking, `next` call order, seek result materialization, key/value reads, removal from DB using a buffered key, unsupported removal without a table, close, null-prefix iteration, and prefixed iterator constraints.

State and persistence behavior: Uses mocked RocksDB state with explicit leak detection and `CodecTestUtil.gc` to check buffer lifecycle after iterator use.

Dependencies and integration points: Depends on RocksDB direct buffer iterator methods, `CodecBuffer` lifetime management, table deletion by `ByteBuffer`, Mockito, and HDDS string/hex utilities for debug output.

Risks: Direct buffers require careful closing; tests assert no leaks but rely on GC-triggered cleanup. Debug `System.out` output is noisy. Prefix matching is only lightly sampled.

Test signals: Good coverage of direct-buffer iterator call order, resource closure, deletion delegation, and prefix iterator behavior.
