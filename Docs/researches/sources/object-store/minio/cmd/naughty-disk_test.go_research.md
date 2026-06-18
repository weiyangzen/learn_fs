# sources/object-store/minio/cmd/naughty-disk_test.go

This test helper wraps a `StorageAPI` and injects deterministic errors by API call number. It is used to simulate disk failures that are hard to reproduce with real storage, such as disk-not-found transitions, mid-operation IO failures, or persistent default failures.

The central type is `naughtyDisk`, containing the wrapped disk, a map from call number to error, an optional default error, a call counter, and a mutex. `newNaughtyDisk` creates the wrapper. `calcError` increments the call number under lock and returns a programmed error, the default error, or nil. Nearly every `StorageAPI` method calls `calcError` first and either returns that error in the method's expected shape or delegates to the real disk.

State is entirely in-memory and test-scoped. The wrapper preserves most real disk behavior when no error is injected, but deliberately overrides `GetDiskLoc` with `-1` indexes and special-cases `IsOnline`: if the injected error is `errDiskNotFound`, it reports true for the equality check path used by callers. `DeleteVersions` expands a single injected error across the returned error slice, and `ReadMultiple` closes the response channel on injected failure.

Dependencies are the broader MinIO storage interfaces and `madmin` scan modes. Risks: because this is a test helper, it can diverge from `StorageAPI` as methods evolve. Coverage signal is indirect; files using this helper define the actual behavioral assertions.
