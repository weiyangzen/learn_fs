# sources/user-network-fs/gcsfuse/internal/storage/dummy_io_bucket.go

## Purpose
`dummy_io_bucket.go` implements a `gcs.Bucket` wrapper that avoids real object-content reads and instead serves zero-filled data with configurable latency. It is useful for dummy IO or performance paths where metadata and write operations still delegate to a real bucket, but data reads should not contact GCS.

## Important APIs, Types, and Functions
`DummyIOBucketParams` carries `ReaderLatency` and `PerMBLatency`. `NewDummyIOBucket` returns nil for nil wrapped buckets or a `dummyIOBucket`. The wrapper delegates metadata, writes, object mutations, folder operations, and naming to the wrapped bucket. `NewReaderWithReadHandle` returns a `dummyReader` for explicit byte ranges. `NewMultiRangeDownloader` returns a `dummyMultiRangeDownloader`.

`calculateLatency` converts bytes and per-MB latency to a duration. `dummyReader` implements `gcs.StorageReader` with total length, bytes read, non-nil read handle, and per-MB latency. `dummyMultiRangeDownloader` uses a wait group and writes zeros to requested outputs asynchronously. `zeroReader` is an infinite zero-producing `io.Reader`.

## Control Flow
`NewReaderWithReadHandle` rejects nil ranges and invalid ranges where `Limit <= Start`, optionally sleeps for fixed reader latency, then returns a reader sized to `Limit - Start`. `dummyReader.Read` returns EOF when exhausted, otherwise chooses the smaller of buffer length and remaining bytes, sleeps according to byte count, advances `bytesRead`, and returns EOF together with the final bytes on the last read.

`dummyMultiRangeDownloader.Add` increments a wait group and launches a goroutine. The goroutine sleeps by `calculateLatency(length, perMBLatency)`, copies exactly `length` zero bytes into the output via `io.Copy` and `io.LimitReader`, and invokes the callback with offset, bytes written, and error. `Close` waits for all added work; `Wait` blocks; `Error` always returns nil; `GetHandle` returns a fixed dummy handle.

## State and Persistence Behavior
The wrapper itself stores only the wrapped bucket and latency settings. Dummy readers store read progress in memory. Multi-range downloader state is only a wait group. No data is persisted and no actual object bytes are read from the wrapped bucket. Writes and metadata mutations still persist wherever the wrapped bucket persists them.

## Dependencies and Integration Points
The file depends on `gcs.Bucket`, `gcs.StorageReader`, `gcs.MultiRangeDownloader`, `cloud.google.com/go/storage` read handles, `context`, `io`, `sync`, and `time`. It is intended to fit transparently anywhere a `gcs.Bucket` is consumed, with special behavior only for content reads.

## Risks and Edge Cases
The read path requires explicit ranges; callers expecting whole-object reads will receive an error. Range validation rejects zero-length ranges because `rangeLen <= 0`, while multi-range downloader accepts zero length. `time.Sleep` ignores context cancellation once a dummy read starts. `dummyMultiRangeDownloader` has no aggregate error state even if `io.Copy` fails, and concurrent writes to the same output are caller-dependent. Returning zero-filled data can hide bugs that depend on real content.

## Test Signals
`dummy_io_bucket_test.go` covers constructor nil behavior, delegated metadata/mutation methods, range validation, reader latency, per-MB latency computation, reader EOF behavior, read handles, multi-range zero data, concurrent add calls, close waiting, latency, fixed handles, and nil error status.
