# sources/user-network-fs/gcsfuse/internal/storage/fake/fake_multi_range_downloader.go

## Purpose
`fake_multi_range_downloader.go` provides a test implementation of `gcs.MultiRangeDownloader` backed by in-memory object data. It supports normal range reads, configurable sleep, default immediate errors, status errors, short reads, and read handles.

## Important APIs, Types, and Functions
`fakeMultiRangeDownloader` stores a fake object, wait group, error fields, sleep duration, short-read flag, and handle. Constructors include `NewFakeMultiRangeDownloader`, `NewFakeMultiRangeDownloaderWithHandle`, `NewFakeMultiRangeDownloaderWithShortRead`, `NewFakeMultiRangeDownloaderWithSleep`, `NewFakeMultiRangeDownloaderWithSleepAndDefaultError`, and `NewFakeMultiRangeDownloaderWithStatusError`. `createFakeObject` converts a `MinObject` plus bytes into the internal object representation.

The interface methods are `Add`, `Close`, `Wait`, `Error`, and `GetHandle`.

## Control Flow
`Add` first handles a configured default error by invoking the callback immediately with zero bytes. Otherwise it validates range inputs similarly to the Google storage reader: negative length errors, offsets beyond size error, offsets less than or equal to negative size map to the whole object, negative offsets count from the end, and positive ranges are truncated to remaining data. Invalid input stores an error and calls the callback immediately.

For valid input, `Add` starts a goroutine, optionally halves length for short-read simulation, sleeps, writes the selected object byte slice to the output, converts short or failed writes to an error, and invokes the callback. `Close` waits and returns the stored error. `Wait` blocks on all goroutines. `Error` returns the configured status error independently of transfer errors. `GetHandle` returns the configured handle.

## State and Persistence Behavior
State is in memory. The downloader holds a copy of object metadata/data and tracks asynchronous transfer completion with a wait group. It has mutable error fields but no locking around `err`, so concurrent failing `Add` calls can race in tests that run with the race detector.

## Dependencies and Integration Points
The file depends on `gcs.MultiRangeDownloader`, `storageutil.ConvertMinObjectToObject`, `io.Writer`, `sync.WaitGroup`, and `time`. It is returned by `fake.Bucket.NewMultiRangeDownloader` and can be directly constructed by tests needing controlled downloader behavior.

## Risks and Edge Cases
The error assignment after goroutine writes appears inverted: `if fmrd.err != nil { fmrd.err = err }` preserves nil rather than recording a new asynchronous write error. There is no mutex for `err`. Short-read mode can invoke callbacks with fewer bytes but nil error if the write itself succeeds, depending on caller expectations. `Error` reports `statusErr`, not transfer errors, so callers must know which method they are validating.

## Test Signals
This subset does not include direct tests for every constructor, but `fast_stat_bucket_test.go` uses `NewFakeMultiRangeDownloader`, and `dummy_io_bucket_test.go` covers a separate dummy downloader. Recommended tests would cover negative offsets, range truncation, default errors, status errors, short reads, handle propagation, and concurrent error recording.
