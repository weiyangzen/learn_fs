<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader.go

Purpose: top-level GCS reader implementation that chooses between a sequential `RangeReader` and a rapid-bucket random-access `MultiRangeReader`, tracks read patterns, serializes range-reader use, and retries short reads for rapid buckets.

Important APIs/types/functions: `ReaderType` enum; `GCSReader`; `GCSReaderConfig`; `NewGCSReader`; `shouldRetryForShortRead`; methods `ReaderName`, `ReadAt`, `read`, `readerType`, `getEndOffset`, `Destroy`, and `CheckInvariants`.

Control flow: `ReadAt` validates offset, builds a `GCSReaderRequest`, calls `read`, and for rapid buckets retries a short read from the remaining offset using `ForceCreateReader`. `read` computes reader type from read classification and bucket type; range-reader reads take a mutex and may recalculate read info after waiting; random reads or skip-size-check reads use MRD. Sequential prefetch end offset is computed from `ReadTypeClassifier`.

State and persistence behavior: no persistent state. In-memory state includes range reader, multi-range reader, read classifier, mutex, object metadata, and bucket reference. Destroy closes child readers and decrements MRD refs.

Dependencies and integration points: implements `gcsx.Reader`; uses `gcsx.ReadTypeClassifier`, metrics read type constants, GCS bucket type rapid/zonal detection, range reader, MRD wrapper, cfg, metrics, and tracing.

Risks: read-type recalculation under lock prevents queued sequential reads from using stale classification. Short-read retry must not retry beyond known object size unless skip size checks is enabled. RangeReader is not used when size checks are skipped. Concurrent random reads bypass the range mutex and rely on MRD concurrency.

Test signals: companion tests cover constructor state, invalid offsets, range reader reuse/reopen, cancellation, inactive timeout reader, zonal random reads, short-read retry, and parallel random reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader.go -->
