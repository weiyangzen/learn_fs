# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneDataStreamOutput.java

Purpose: This public byte-buffer output wrapper exposes Ozone data-stream writes while preserving optional `Syncable`, metadata, multipart, and pre-commit behavior from the underlying stream.

Important APIs and types: Main methods are constructors for syncable and byte-buffer outputs, `write(ByteBuffer,int,int)`, `flush`, `close`, `hsync`, `hflush`, `getCommitUploadPartInfo`, `getKeyDataStreamOutput`, `setPreCommits`, `getByteBufStreamOutput`, and `getMetadata`. It uses `ByteBufferStreamOutput`, `Syncable`, `KeyCommitOutput`, `KeyDataStreamOutput`, `CryptoOutputStream`, and `CipherOutputStreamOzone`.

Control flow: Writes and close/flush delegate to the wrapped `ByteBufferStreamOutput`. Hsync either degrades to flush when disabled, or flushes the byte-buffer stream before invoking the syncable target. Commit-related calls unwrap nested `OzoneOutputStream`, Hadoop crypto, or Ozone cipher wrappers to find a `KeyCommitOutput` or `KeyDataStreamOutput`.

State and persistence behavior: State is the wrapped byte-buffer output, selected syncable, and `enableHsync` flag. Persistent key data and OM commit state are controlled by the wrapped implementation.

Dependencies and integration points: Returned by `ClientProtocol.createStreamKey`, multipart stream APIs, and stream file APIs. It bridges public client code with internal key data-stream implementations and encryption wrappers.

Risks: The `OzoneDataStreamOutput(Syncable, boolean)` constructor requires the syncable to also be an `OzoneDataStreamOutput`, which is stricter than the doc wording. `getMetadata` blindly casts the byte-buffer stream to `KeyMetadataAware`. Hsync behavior depends on feature flag configuration and wrapper identity.

Test signals: Tests should cover direct and wrapped `KeyDataStreamOutput` discovery, pre-commit forwarding, hsync disabled versus enabled behavior, flush before external syncable hsync, metadata passthrough, multipart commit info forwarding, and unsupported/incompatible stream failures.
