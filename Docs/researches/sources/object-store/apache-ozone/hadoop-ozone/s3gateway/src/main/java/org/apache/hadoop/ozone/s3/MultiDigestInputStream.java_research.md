# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/MultiDigestInputStream.java

Purpose: `MultiDigestInputStream` wraps an input stream and updates multiple `MessageDigest` instances in a single pass, allowing S3 uploads to compute ETag MD5 and optional payload SHA-256 without rereading the body.

Important APIs and flow: constructors register provided digest instances by algorithm. `read()` and `read(byte[], int, int)` delegate to the wrapped stream and update all digests when enabled. `on(boolean)` toggles digest updates, `getMessageDigest`, `getAllDigests`, `resetDigests`, `setMessageDigest`, `addMessageDigest`, and `removeMessageDigest` expose digest management.

State, dependencies, risks, and tests: mutable state is the digest map and the `on` flag; no persistence exists. It integrates with `EndpointBase.getS3ChunkInputStreamInfo` and object upload verification. Risks include digest algorithm name collisions, callers mutating returned digest instances, no synchronization for concurrent reads, and single-byte `read()` casting signed bytes while `MessageDigest.update(byte)` accepts raw byte value. Tests should cover byte and buffer reads, toggling, resets, multiple algorithms, and empty stream behavior.
