## sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_bucket.go

### Purpose
`throttled_bucket.go` wraps a `gcs.Bucket` to rate-limit GCS operations and object read bandwidth.

### Important APIs, Types, And Functions
`NewThrottledBucket(opThrottle, egressThrottle, wrapped)` returns a `gcs.Bucket`. `throttledBucket` implements bucket methods. `throttledGCSReader` combines a throttled `io.Reader` with the original `gcs.StorageReader` close/read-handle behavior.

### Control Flow
Most bucket methods call `opThrottle.Wait(ctx, 1)` before delegating to the wrapped bucket. `NewReaderWithReadHandle` additionally wraps successful readers with `ThrottledReader` using `egressThrottle`. `FinalizeUpload` and `FlushPendingWrites` intentionally skip op throttling to avoid risking data loss after a write has started. `NewMultiRangeDownloader` also delegates without throttling in this file.

### State, Persistence, And Dependencies
State consists of two throttles and the wrapped bucket. Persistent effects are the wrapped bucket's GCS operations. Dependencies include `internal/storage/gcs`, Cloud Storage read handles, `io`, and context.

### Integration Points
This wrapper composes around real, monitored, or cached buckets to enforce configured operation and bandwidth limits. It preserves folder, object, reader, and write APIs in the `gcs.Bucket` interface.

### Risks
Skipping throttling for finalize/flush is deliberate but means write-heavy traffic can still create unthrottled requests after writer creation. `NewMultiRangeDownloader` is not op-throttled or egress-throttled here, so multi-range paths require separate metrics/limits if desired. Read bandwidth throttling limits only calls through the returned reader.

### Test Signals
No direct throttled bucket tests are present in this shard. Reader-level throttling is covered by `throttle_reader_test.go`; operation-level bucket method coverage would require a fake bucket and fake throttle.
