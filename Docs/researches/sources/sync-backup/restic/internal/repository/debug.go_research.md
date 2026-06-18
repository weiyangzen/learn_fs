## sources/sync-backup/restic/internal/repository/debug.go

Purpose: debug-build utilities for inspecting, dumping, repairing, extracting, and reuploading repository pack/index contents.

Important APIs/types: `packDumpEntry` and `packDumpBlob` define JSON dump shapes. `writePackDumpJSON` writes indented JSON. `DumpPacks` lists pack files in parallel and dumps header blob layout. `DumpIndexes` loads every index and dumps JSON. `ExaminePackOptions` controls repair/extract/reupload behavior. `ExaminePack` loads a pack, compares content hash, inspects index entries, reads pack header, and loads blobs. `checkPackSize` compares blob offsets/header size with file size. `tryRepairWithBitflip` brute-forces one-bit or one-byte repairs with worker goroutines. `decryptUnsigned` decrypts without MAC verification. `loadBlobs` decrypts/decompresses blobs, optionally stores plaintext or reuploads. `storePlainBlob` writes plaintext blobs to local files.

Control flow and state: this file is behind the `debug` build tag. Repair search uses shared `found`/`fixed` variables and closes a `done` channel on success. Extraction writes files in the current working directory with prefixes such as `correct-`, `wrong-hash-`, `damaged-`, and `repaired-`.

Dependencies and integration points: integrates repository raw loading, pack listing, index iteration, crypto internals, zstd decompression, uploader APIs, progress printers, and OS file creation. It is intended for manual diagnostics rather than normal command paths.

Risks and test signals: debug utilities can write decrypted user data to disk and reupload blobs, so they are powerful and sensitive. The bitflip repair path is CPU-heavy and concurrency-sensitive. This target set has no direct tests for debug behavior.
