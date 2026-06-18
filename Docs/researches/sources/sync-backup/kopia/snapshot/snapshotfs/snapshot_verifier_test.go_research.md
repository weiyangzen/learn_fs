# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_verifier_test.go

Purpose: integration tests for verifier success, enqueue errors, full file reads, missing blob detection, and max-error limiting.

Important APIs/types/functions: `TestSnapshotVerifier`, `snapshotfs.NewVerifier`, `VerifierOptions`, `InParallel`, `DirectoryEntry`, `blob.ReadBlobMap`, and repository blob deletion.

Control flow: the test uploads a directory with three files, opens another repository handle, then runs subtests for enqueue errors, positive blob-map verification, full reads with blob map, missing pack blobs in the blob map, `MaxErrors=1`, and missing underlying blobs without a blob map.

State and persistence: writes real repository objects, flushes, reads blob maps, mutates an in-memory blob map, and deletes pack blobs in the final scenario.

Dependencies and integration points: covers verifier, tree walker, repository object verification, blob storage, uploader, and error aggregation.

Risks and test signals: subtests use separate verifier instances except where zero-stat runs are intentional. Signals include error counts, specific missing-blob messages, nonzero processed/read stats, and max-error truncation.
