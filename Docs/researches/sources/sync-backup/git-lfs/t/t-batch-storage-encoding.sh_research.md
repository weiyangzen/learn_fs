# sources/sync-backup/git-lfs/t/t-batch-storage-encoding.sh

## Purpose
Tests HTTP transfer encoding behavior for LFS object storage. It covers gzip and zstd downloads, zstd concurrency and resume behavior, invalid configured encodings, chunked upload transfer encoding, and normal content-length uploads.

## Important APIs, Functions, and Control Flow
Repository names and object contents trigger special server behavior. Download tests configure `lfs.transfer.httpDownloadEncoding`, remove local object caches, run `git lfs pull` or `fetch` with curl tracing, and count `Accept-Encoding`, `Content-Encoding`, decompression, zstd decoder lifecycle, Range, and Content-Range lines. Upload tests inspect PUT request headers after filtering trace output to the storage request.

## State, Persistence, and Dependencies
The script mutates Git config, local object caches, remote repositories, and trace logs. It depends on curl verbose output, server behavior keyed by content/repository names, and object assertions.

## Integration Points, Risks, and Test Signals
Integration points are the HTTP storage adapter, retry/resume code, zstd decoder pooling, and upload header construction. Signals are exact header counts, successful local/server object assertions, unsupported encoding error text, and resume logs. Risks are trace formatting changes, optional zstd support assumptions, and concurrent decoder count sensitivity.
