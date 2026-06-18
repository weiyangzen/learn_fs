# sources/sync-backup/kopia/repo/blob/storage_test.go

Purpose: unit tests for blob package helper functions and metadata utilities.

Important APIs/types/functions: covers `ListAllBlobs`, `IterateAllPrefixesInParallel`, `EnsureLengthExactly`, `IDsFromMetadata`, `MaxTimestamp`, `MinTimestamp`, `TotalLength`, `DeleteMultiple`, `Metadata.String`, and `PutBlobAndGetMetadata` using in-memory `blobtesting.NewMapStorage`.

Control flow: tests populate map storage, list by prefixes, collect concurrent callback results under a mutex, inject callback errors, validate range-length outcomes, compute metadata aggregates, delete selected IDs in parallel, compare JSON formatting, and verify put metadata uses the storage-assigned fixed timestamp.

State and persistence behavior: all state is in-memory `blobtesting.DataMap` and optional key-time maps. `DeleteMultiple` mutates the map by removing selected blob IDs.

Dependencies/integration: depends on blobtesting, gather buffers, testify assertions, and the public blob package.

Risks and edge cases: concurrent prefix iteration requires test callback locking, mirroring real caller obligations. Tests do not cover invalid `DeleteMultiple` parallelism.

Test signals: failures indicate broken helper semantics that would affect every provider and repository maintenance path.
