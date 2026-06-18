
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneOutputStreamStub.java

Purpose: test `OzoneOutputStream` wrapper for in-memory output streams, especially multipart part commits.

Important APIs and control flow: delegates `write`, `flush`, and idempotent `close` to the wrapped output stream. After close, `getCommitUploadPartInfo` returns part name plus ETag from `KeyMetadataAware` metadata; before close it returns `null`.

State, dependencies, integration: tracks part name and close state. Used by `OzoneBucketStub.createMultipartKey` and normal key paths that need a concrete `OzoneOutputStream`.

Risks and test signals: casts the wrapped stream to `KeyMetadataAware`, so callers must supply compatible streams. It does not model asynchronous commit or failure after close. Multipart endpoint utilities use returned ETags for completion requests.
