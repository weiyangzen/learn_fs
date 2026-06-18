# sources/user-network-fs/gcsfuse/internal/cache/data/file_info_test.go

## Purpose
This file tests file-cache metadata key construction and size accounting. It documents the expected string key format and the distinction between logical content size and rounded physical cache size.

## Important APIs, Types, And Functions
Constants define a test bucket, object, generation, epoch time, file size, and expected key. `getTestFileInfoKey` builds a reusable `FileInfoKey`. Tests cover `FileInfoKey.Key`, invalid key fields, `NewFileInfo`, `ContentSize`, and `Size`.

## Control Flow And State
The key test verifies concatenation of bucket name, Unix creation time, and object name. Empty bucket or object name returns `InvalidKeyAttributes` and an empty key. `ContentSize` returns the file content size for a non-sparse `FileInfo`. `Size` rounds a 23-byte file up to a 4096-byte block size.

## State And Persistence Behavior
The suite is entirely in memory. It creates `FileInfo` values but no cache files.

## Dependencies And Integration Points
It uses `testing`, `time`, `fmt`, and `testify/assert`. It indirectly validates the `diskutil` integration via `FileInfo.Size`.

## Risks And Edge Cases
Sparse-mode `ContentSize`, nil `DownloadedChunks`, zero or one block size, and cache-key collision concerns are not covered here. Those behaviors are covered only indirectly elsewhere.

## Test Signals
The tests provide basic correctness checks for stable key naming and LRU size accounting.
