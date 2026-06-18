# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/CodecTestUtil.java

## Purpose
Provides reusable assertions for testing HDDS database `Codec` implementations, including codec-buffer and persisted-format behavior.

## Important APIs, types, and functions
- Public helpers include `runTest`, `newCodecWithoutCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `getTypeClass`, `copyObject`, and `gc`.
- Uses `Codec`, `CodecBuffer`, `ByteBuffer`, weak references, and logging.
- Checks object equality, serialized byte behavior, copied object behavior, and buffer cleanup expectations.

## Control flow
`runTest` executes a codec through persisted-format conversion, object restoration, optional object copy, type-class verification, and buffer lifecycle checks. Helper wrappers adapt codecs that do not support `CodecBuffer` directly.

## State and persistence behavior
The byte arrays and buffers represent persisted database values, but tests remain in memory. `gc` and weak references are used to probe object/buffer retention behavior.

## Dependencies and integration points
HDDS metadata stores rely on codecs for RocksDB/table serialization. This utility standardizes codec contract tests.

## Risks and test signals
Codec bugs can corrupt persisted metadata or leak buffers. This helper gives shared signals for serialization fidelity, copy semantics, and buffer cleanup.
