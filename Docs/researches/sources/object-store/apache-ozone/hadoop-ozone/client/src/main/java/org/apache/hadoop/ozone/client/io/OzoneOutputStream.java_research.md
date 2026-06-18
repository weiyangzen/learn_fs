# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneOutputStream.java

Purpose: This public byte-array output wrapper exposes Ozone key writes as an `OutputStream` with optional Hadoop `Syncable`, metadata access, multipart commit info, pre-commit forwarding, and hsync behavior.

Important APIs and types: Important methods are constructors, `write`, `flush`, `close`, `hflush`, `hsync`, `getCommitUploadPartInfo`, `getOutputStream`, `getKeyOutputStream`, `setPreCommits`, and `getMetadata`. It unwraps Hadoop `CryptoOutputStream` and `CipherOutputStreamOzone` to find `KeyOutputStream`, `KeyCommitOutput`, or `KeyMetadataAware`.

Control flow: Writes/flush/close delegate to the wrapped output. Hsync flushes when disabled; when enabled it flushes the wrapper if the syncable target is separate, then calls `syncable.hsync`. Commit-related methods unwrap encryption layers before forwarding to the internal key stream.

State and persistence behavior: State is the wrapped output stream, optional syncable, and hsync feature flag. Data persistence and OM commit are performed by the wrapped stream during close or sync.

Dependencies and integration points: Returned by `ClientProtocol.createKey`, multipart create, and file create APIs. It is the main public wrapper around `KeyOutputStream` and encrypted output streams.

Risks: Metadata and pre-commit calls fail at runtime if the wrapped stream is not backed by the expected interfaces. Hsync silently behaves as flush when disabled, preserving prior behavior but potentially surprising callers expecting durability. `getKeyOutputStream` only finds direct unwrapped `KeyOutputStream`, not other `KeyCommitOutput` implementations.

Test signals: Tests should cover write/flush/close delegation, hsync enabled/disabled paths, encrypted stream unwrapping, metadata propagation, pre-commit forwarding, multipart commit info forwarding, and unsupported wrapped-stream error messages.
