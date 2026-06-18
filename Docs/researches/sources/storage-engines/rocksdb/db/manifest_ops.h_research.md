<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.h -->
# sources/storage-engines/rocksdb/db/manifest_ops.h

## Purpose
Declares the helper for resolving the active MANIFEST path from a DB's `CURRENT` file.

## Important APIs, Types, And Functions
`GetCurrentManifestPath()` takes a DB name, `FileSystem*`, retry flag, output manifest path, and output manifest file number. The comment documents that `is_retry=true` enables stronger `verify_and_reconstruct_read` behavior for perceived corruption cases.

## Control Flow
The header defines a single synchronous read/parse helper contract. Callers use it when they need the descriptor file path before opening or re-reading a manifest.

## State And Persistence Behavior
The API reads persistent metadata through the filesystem and returns parsed results by output pointer. It does not mutate DB files.

## Dependencies And Integration Points
Includes `<cassert>` and `rocksdb/env.h` for `Status` and `FileSystem`. It belongs to manifest/version-set recovery utilities and is implemented in `manifest_ops.cc`.

## Risks And Edge Cases
The raw pointer outputs must be valid. Because this helper reports corruption for malformed `CURRENT`, callers should distinguish read IO errors from metadata corruption. Retry behavior depends on filesystem support for the reconstruct-read option.

## Test Signals
Coverage should validate successful path construction and all corruption cases in `manifest_ops.cc`, plus retry-mode behavior in filesystem mocks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manifest_ops.h -->
