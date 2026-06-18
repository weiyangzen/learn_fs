# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/file_blob.rs

Purpose: Represents regular file blobs.

Important APIs/types/functions: `new`, `create_blob`, `blob_id`, `num_bytes`, `resize`, `try_read`, `write`, `flush`, `parent`, `set_parent`, `remove`, `lstat_size`, and `all_blocks`. Test-only helpers expose node count and raw blob extraction.

Control flow: all file data operations delegate to `BaseBlob` data APIs, which offset past the fsblob header. Creation stores `BlobType::File` with empty data. Removal consumes the wrapper and removes the base blob directly.

State and persistence behavior: no extra file metadata lives here beyond the base header and raw data payload. Size is the base data length. Flush delegates to the underlying blob flush.

Dependencies and integration points: constructed by `FsBlobStore` and `FsBlob::parse`; used through `FsBlob::File` and `ConcurrentFsBlob`.

Risks: file-level timestamps and ownership are not stored here; they live in parent directory entries. Callers must update parent directory metadata when file content changes. `try_read` semantics depend on lower-layer blob behavior.

Test signals: useful tests include read/write offset handling, resize truncation/extension, lstat size, parent updates, and remove not attempting a writeback.
