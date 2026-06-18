# sources/sync-backup/restic/internal/backend/gs/gs.go

Purpose: Implements the restic backend interface for Google Cloud Storage.

Important APIs and types: `gs` stores the storage client, project ID, connection count, bucket name, region, bucket handle, and layout. `NewFactory`, `Open`, `Create`, `Save`, `Load`, `Stat`, `Remove`, `List`, `Delete`, `Close`, `Warmup`, `WarmupWait`, `Hasher`, `Properties`, `IsNotExist`, and `IsPermanentError` implement backend behavior. Helpers include `getStorageClient`, `bucketExists`, `open`, and `openReader`.

Control flow and state: `getStorageClient` builds an HTTP client using the supplied transport and either `GOOGLE_ACCESS_TOKEN` or Google default credentials. `Create` checks bucket existence, tolerates forbidden bucket-attrs access as possible existing bucket, and creates a bucket when missing. `Save` disables resumable upload chunking, streams data, sets MD5, closes the writer, and checks byte count. `Load` delegates to `util.DefaultLoad` and range reader validation. `List` iterates objects by layout prefix and calls the callback with basename/size.

Persistence and dependencies: Data persists as GCS objects using the default restic layout. Dependencies include `cloud.google.com/go/storage`, OAuth2/google auth, `googleapi`, `layout`, `location`, `util`, and restic backend abstractions.

Integration points: Registered through `NewFactory` and aggregate backend registry. It supports generic backend tests and repository operations. MD5 hasher support enables upload validation.

Risks and test signals: Risks include credential/environment handling, forbidden bucket-existence checks masking missing buckets, range-too-short classification, rate-limit behavior from disabled chunking, and object listing cancellation. `gs_test.go` runs the generic backend suite when GCS credentials are available; config tests cover parsing.
