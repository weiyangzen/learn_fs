
# sources/sync-backup/restic/internal/repository/repair_index_test.go

Purpose: tests `RepairIndex` against common repository index damage scenarios.

`listIndex` lists index file IDs. `testRebuildIndex` creates random blobs, records old indexes, applies a damage function, reopens the backend, runs `RepairIndex` with either normal or `ReadAllPacks` mode, and validates the repository with `TestCheckRepo`. `TestRebuildIndex` runs scenarios for a valid index, damaged index bytes, a missing index file, and a missing pack file.

State and persistence are real backend mutations: files are damaged via `replaceFile` or removed. Integration points include repository reopen, index load callbacks, pack scanning, index rewrite, and checker validation. Risks covered include failure to recover from damaged indexes, dangling pack references, and mode differences between incremental repair and full pack reread.
