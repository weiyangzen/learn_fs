# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/AsyncFileBlobStore.h

Purpose: adapts blob-store objects to the `IAsyncFile` interface for backup/restore style reads and writes.

Important APIs and types: `joinErrorGroup` propagates the first async error through a shared promise. `AsyncFileBlobStoreWrite` is append-only/sequential and implements multipart upload. Nested `Part` buffers content, tracks length, and computes MD5 or SHA256 base64 checksums. `AsyncFileBlobStoreRead` is read-only and delegates reads/size to `IBlobStoreEndpoint`.

Control flow: writes require `offset == m_cursor`, append bytes into the current part, and when minimum part size is reached call `endCurrentPart` to throttle via `FlowLock` and start an async upload. `sync()` finalizes once: single-part writes use `writeEntireFileFromBuffer`, multipart writes await all ETags and call `finishMultiPartUpload`.

State and persistence: write state includes bucket/object names, cursor, upload ID, finish future, part vector, error promise, and upload concurrency lock. Persistence is remote blob object storage; incomplete or failed multipart uploads are canceled by futures but may need endpoint cleanup.

Dependencies and integration: uses `IAsyncFile`, packet queues, rate/flow primitives, `IBlobStoreEndpoint`, MD5/SHA256, base64, and trace events. Backup containers use these adapters for blob-backed files.

Risks: non-sequential writes fail; `flush()` intentionally does not upload partial data. Checksum finalization is one-shot. Error fanout must prevent later parts from masking earlier failures. Read-zero-copy is unsupported.

Test signals: integration tests for blob backup/read/write and multipart restore paths; trace `AsyncFileBlobStoreMultipartUploadChecksum` helps inspect multipart integrity metadata.
