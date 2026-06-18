# sources/sync-backup/git-lfs/lfs/gitscanner_catfilebatch.go

Purpose: loads Git blobs by SHA and detects whether their content is an LFS pointer.

Important APIs/types/functions: `runCatFileBatch`, `PointerScanner`, `NewPointerScanner`, `Scan`, `Pointer`, `BlobSHA`, `ContentsSha`, `Err`, `Close`, and `next`.

Control flow: `runCatFileBatch` consumes blob SHA strings, scans each with `PointerScanner`, sends decoded pointers, reports lockable non-pointers, propagates errors, waits on upstream channels, closes scanner and output channels. `PointerScanner.next` loads the object, hashes contents, buffers only blobs below `blobSizeCutoff`, decodes pointers for small blobs, and records either pointer OID or content hash.

State/persistence behavior: read-only object database access, but owns scanner resources and channels.

Dependencies/integration: built on `git.ObjectScanner`, `DecodePointer`, SHA-256, and lockable name lookup. Used by ref, index, and tree scanners.

Risks/test signals: large blobs are never pointer-decoded by design. Exact-size reads are enforced. Tests cover valid pointer interleaved with random data and large blob hash behavior.
