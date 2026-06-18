# sources/sync-backup/restic/internal/backend/cache/file_test.go

Purpose: Tests low-level cache file operations.

Important APIs and helpers: `generateRandomFiles`, `randomID`, `load`, `listFiles`, and `clearFiles` exercise `Cache.save`, `load`, `Has`, `list`, and `Clear`. Tests include `TestFiles`, `TestFileLoad`, `TestFileSaveConcurrent`, and `TestFileSaveAfterDamage`.

Control flow and state: Tests generate random cache files for snapshot, pack, and index types, validate hashes after reload, compare listed IDs, clear all but selected IDs, and verify range reads with offsets and lengths. Concurrent save/load simulates multiple restic processes writing the same handle and tolerates either temporary not-exist or correct data while writes race.

Dependencies and integration: Uses `restic.Hash`, random data helpers, `errgroup`, OS file removal, runtime Windows skip for concurrency semantics, and `TestNewCache`.

Risks and test signals: Guards cache layout, atomic temp-file save, range slicing, clearing semantics, concurrent writers, and failure after the cache directory is removed.
