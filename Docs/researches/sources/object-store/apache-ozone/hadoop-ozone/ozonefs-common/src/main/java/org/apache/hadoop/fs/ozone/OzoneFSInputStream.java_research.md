<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSInputStream.java

## Purpose
Hadoop `FSInputStream` wrapper for Ozone key input streams with byte counting, tracing, byte-buffer reads, unbuffer support, and positioned byte-buffer reads.

## Important APIs, types, and functions
Implements `ByteBufferReadable`, `CanUnbuffer`, and `ByteBufferPositionedReadable`. Key methods include single-byte and array reads, `seek`, `getPos`, `skip`, `available`, `read(ByteBuffer)`, `unbuffer`, `read(long, ByteBuffer)`, and `readFully(long, ByteBuffer)`.

## Control flow
Normal reads delegate to the wrapped input and increment Hadoop statistics. ByteBuffer reads prefer a wrapped `ByteBufferReadable`; otherwise they read via the backing array or a temporary byte array. Positioned reads prefer `ExtendedInputStream.readFully(position, buf)`; fallback saves the old position, seeks, reads via `ByteBufferReadable`, handles EOF as `-1`, and seeks back in `finally`.

## State and persistence behavior
The wrapper holds an input stream and optional statistics object. It does not cache data or persist state; it mutates the wrapped stream cursor during seek/fallback positioned reads.

## Dependencies and integration points
Used by `FSDataInputStream` from Ozone filesystem `open`. It integrates with Ozone `KeyInputStream`, Hadoop crypto streams, byte-buffer APIs, and tracing.

## Risks and test signals
Fallback `read(ByteBuffer)` uses `available()` to size reads, which can be surprising for streams where availability is not remaining length. Positioned-read fallback assumes the wrapped stream is both `Seekable` and `ByteBufferReadable`. Existing tests cover heap/direct ByteBuffer reads, EOF position preservation, capability wrapping, and crypto unbuffer forwarding; further tests should cover positioned direct-buffer reads and statistics increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSInputStream.java -->
