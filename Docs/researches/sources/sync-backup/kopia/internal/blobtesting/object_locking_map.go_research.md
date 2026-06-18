## sources/sync-backup/kopia/internal/blobtesting/object_locking_map.go

Purpose: in-memory versioned object-locking storage for testing retention and delete-marker behavior.

Important APIs/types/functions: `ErrBlobLocked`, `RetentionStorage`, `NewVersionedMapStorage`, `objectLockingMap`, `GetBlob`, `GetMetadata`, `GetRetention`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, and `TouchBlob`.

Control flow, state, and persistence: each put appends a new version entry with value, mtime, and optional retention parameters. Deletes append a delete marker unless already absent/deleted. Reads and lists use only the latest non-delete-marker version. Touch respects retention and returns `ErrBlobLocked` while locked. All state is in-memory behind an RW mutex.

Dependencies and integration points: simulates S3-style object locking for provider tests and generic storage verification with retention options.

Risks and test signals: `DeleteBlob` does not check retention before adding a delete marker, so it may not fully mimic locked-object deletion rules. Tests run generic storage verification with governance retention but do not deeply assert version histories.
