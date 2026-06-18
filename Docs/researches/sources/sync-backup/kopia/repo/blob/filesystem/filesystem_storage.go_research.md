# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage.go

Purpose: implements filesystem-backed blob storage through the sharded storage adapter.

Important APIs/types/functions: `fsStorage`, `fsImpl`, `isRetriable`, `GetBlobFromPath`, `GetMetadataFromPath`, `PutBlobInPath`, `createTempFileWithData`, `createTempFileAndDir`, `DeleteBlobInPath`, `ReadDir`, `TouchBlob`, `ConnectionInfo`, `DisplayName`, `New`, and provider `init`.

Control flow: reads retry retriable OS path/link errors, open the target file, seek/copy requested ranges, handle macOS zero-size transient reads specially, and enforce exact length. Metadata stats the path under retry. Writes reject unsupported retention/DoNotRecreate, create a unique temp file with random suffix, create missing shard directories, write/sync/close data, atomically rename, optionally chown, set mod time, and return server mod time. Deletes retry removes and ignore missing files. Listing converts directory entries to file infos while ignoring races where entries disappear. `TouchBlob` updates old mtimes through sharded path resolution. `New` optionally creates the root directory, verifies accessibility, and wraps `fsImpl` in `sharded.New`.

State and persistence behavior: blob data persists as files under a sharded directory tree. Temporary files are removed on write/sync/close errors. Atomic rename is the main consistency boundary.

Dependencies/integration points: uses `osInterface` for real/mocked OS calls, `dirutil.MkSubdirAll`, `retry`, `iocopy`, `clock`, and the blob registry. Risks include filesystem-specific stale/path errors, partial temp cleanup failures, chmod/chown limitations, exact-length races, and unsupported retention/DoNotRecreate. Tests cover shared storage behavior, concurrency, sharding, retries, error handling, temp file cleanup, sync-before-close, Unix stale errors, and capacity by platform.
