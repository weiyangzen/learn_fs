
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneDataStreamOutputStub.java

Purpose: test `OzoneDataStreamOutput` wrapper that delegates to an in-memory `ByteBufferStreamOutput`.

Important APIs and control flow: `write(ByteBuffer, off, len)`, `flush`, and `close` forward to the underlying stream; close is idempotent. `getCommitUploadPartInfo` returns `null` until closed, then returns part name and ETag metadata. `getKeyDataStreamOutput` exposes the underlying stream when it implements `KeyDataStreamOutput`.

State, dependencies, integration: tracks `partName` and `closed` flag. Used by `OzoneBucketStub` for streaming key and streaming multipart paths.

Risks and test signals: assumes metadata is available through the superclass/underlying output. Behavior is simpler than real data stream commit semantics, so tests using it validate endpoint logic, not datanode streaming. Multipart tests indirectly exercise commit-part info.
