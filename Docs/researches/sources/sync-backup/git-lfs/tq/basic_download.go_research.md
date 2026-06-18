# sources/sync-backup/git-lfs/tq/basic_download.go

Purpose: basic HTTP download adapter with resume support, hash verification, optional zstd decompression, and atomic-ish rename into place.

Important APIs/types/functions: `basicDownloadAdapter`, worker context with zstd decoder, `tempDir`, `DoTransfer`, `downloadFilename`, `download`, `configureBasicDownloadAdapter`, and `makeRequest`.

Control flow: reserves a temp file, moves any `.part` resume file into it, hashes existing bytes, validates resume range, issues GET/Range request, handles network/416/429 retry cases, validates 206 Content-Range for resumes, optionally decodes zstd, copies through a hashing reader with progress callbacks, compares SHA/OID, closes, and renames to final path.

State and persistence: uses `$LFSStorageDir/incomplete`, `.part` files for resume, temp files for in-progress data, and per-worker zstd decoder.

Dependencies and integration points: registered as `basic` download adapter in the manifest; uses `tools.TempFile`, `RobustRename`, `HashingReader`, `RetriableReader`, `CopyWithCallback`, and `RenameFileCopyPermissions`.

Risks: resume correctness depends on server Content-Range compliance. Existing final file from another process is treated as success after rename failure check. Zstd decoder reuse is per worker and must be closed. Hash mismatch discards partial via deferred cleanup unless moved to `.part` earlier.

Test signals: no dedicated basic-download tests in this subset; queue and transfer integration exercise adapter selection.
