# sources/sync-backup/kopia/repo/maintenance/blob_retain_test.go

Purpose: integration tests retention extension against repository environments with and without configured retention.

Important APIs/types/functions: `TestExtendBlobRetentionTime`, `TestExtendBlobRetentionTimeDisabled`, `maintenance.ExtendBlobRetentionTime`, fake clock, and retention-capable storage test helpers.

Control flow: tests create repositories, write one object, flush blobs, inspect retention metadata, advance time, run the extension task, and assert stats plus updated expiry. The disabled case verifies no stats and continued ability to touch blobs.

State/persistence behavior: creates temporary repository blob state and mutates retention metadata in the test storage.

Dependencies/integration: uses `repotesting`, `faketime`, `blobtesting.RetentionStorage`, `cache.Storage`, object writers, and fixed crypto test keys.

Risks/test signals: catches failure to include newly written blobs in extension scope and ensures disabled retention is a no-op. It assumes a fixed number of blobs after writing.
