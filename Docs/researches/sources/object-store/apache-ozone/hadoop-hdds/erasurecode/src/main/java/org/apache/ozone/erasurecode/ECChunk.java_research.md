<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/ECChunk.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/ECChunk.java

## Purpose
`ECChunk` is the lightweight chunk wrapper used by the erasure-code layer to pass either full buffers or slices of buffers into raw encoders and decoders. It normalizes byte arrays into `ByteBuffer` and carries an `allZero` flag used by lower-level coder utilities to avoid depending on caller-filled data for known-zero chunks.

## Important APIs, Types, and Functions
The class exposes constructors for `ByteBuffer`, `ByteBuffer` plus offset/length, `byte[]`, and `byte[]` plus offset/length. Important methods are `getBuffer()`, `isAllZero()`, `setAllZero(boolean)`, static `toBuffers(ECChunk[])`, and test-oriented `toBytesArray()`. The offset/length ByteBuffer constructor duplicates the source, sets position and limit, and slices to isolate the visible range.

## Control Flow
Construction is a direct wrapping flow with no background work. `toBuffers` iterates through chunks, preserving `null` entries for erased or unused inputs, while `toBytesArray` marks, drains remaining bytes into a new array, and resets the position.

## State and Persistence Behavior
State is only the wrapped `ByteBuffer` reference and the mutable `allZero` flag. There is no persistence; buffer content and position are owned by the caller/coder interaction and may advance during encode/decode calls.

## Dependencies and Integration Points
The class depends only on `java.nio.ByteBuffer` and integrates with `RawErasureEncoder`, `RawErasureDecoder`, `CoderUtil.toBuffers`, and the erasure-code tests that compare `ECChunk` payloads.

## Risks and Test Signals
Risks include shared mutable ByteBuffer state, callers expecting `toBytesArray()` to consume without position changes, and offset/length errors causing `IllegalArgumentException` from ByteBuffer bounds. Tests should cover byte-array wrapping, sliced ByteBuffer wrapping, `null` preservation in arrays, all-zero flag handling through `CoderUtil`, and position stability after `toBytesArray()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/ECChunk.java -->
