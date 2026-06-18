# sources/user-network-fs/gcsfuse/internal/cache/data/file_info.go

## Purpose
This file defines file-cache metadata used by the LRU and cache handlers. It provides stable cache keys, cache value sizing, sparse-mode downloaded-byte accounting, and local file path/permission specs.

## Important APIs, Types, And Functions
`InvalidKeyAttributes` is the error message for missing key fields. `FileInfoKey` stores bucket name, bucket creation time, and object name; `Key` delegates to `GetFileInfoKeyName`. `GetFileInfoKeyName` concatenates bucket name, bucket creation Unix time, and object name using preallocated byte storage.

`FileInfo` stores key, object generation, offset, file size, sparse-mode flag, optional `DownloadedChunks`, and cache-directory volume block size. Methods `ContentSize` and `Size` support logical content accounting and LRU `ValueType` size accounting. `FileSpec` carries local cache path and permissions. `NewFileInfo` centralizes field initialization.

## Control Flow And State
Key generation fails if bucket or object name is empty. For non-sparse files, `ContentSize` returns `FileSize`. For sparse files with a `DownloadedChunks` map, it returns downloaded chunk bytes instead of full object size. `Size` passes `ContentSize` to `diskutil.GetSpeculativeFileSizeOnDisk`, rounding by cache volume block size.

## State And Persistence Behavior
`FileInfo` is an in-memory cache value and describes persistent local cache files, but it does not perform I/O. `Offset` has two meanings: downloaded prefix length for non-sparse mode and `MaxUint64` sentinel in sparse mode as initialized by `CacheHandler`.

## Dependencies And Integration Points
The file depends on `diskutil` for physical-size estimation and on `ByteRangeMap` for sparse downloads. `CacheHandler`, `CacheHandle`, downloader jobs, and the LRU cache use these types to validate generations, offsets, cache size, and local file paths.

## Risks And Edge Cases
The key format is simple concatenation without separators, so it relies on bucket creation time and names being sufficient to avoid practical ambiguity. `FileInfoKey.Key` does not pass `BucketCreationTime` in some callers that construct only bucket/object names, making the Unix value zero in those contexts. Sparse `ContentSize` returns full file size if `DownloadedChunks` is nil, which is a fallback that can overstate sparse occupancy.

## Test Signals
`file_info_test.go` validates key generation errors and size rounding. `file_info_benchmark_test.go` tracks the optimized key-generation path.
