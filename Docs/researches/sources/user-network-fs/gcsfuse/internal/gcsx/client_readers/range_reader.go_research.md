<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader.go

Purpose: sequential GCS reader that reuses a single `NewReaderWithReadHandle` stream, prefetches ranges, skips small forward gaps, propagates cancellation, records read metrics, and converts object-not-found during open into stale-file-handle errors.

Important APIs/types/functions: constants `MiB` and `maxReadSize`; type `RangeReader`; constructor `NewRangeReader`; methods `checkInvariants`, `destroy`, `closeReader`, `ReadAt`, `readFromRangeReader`, `readFull`, `startRead`, `skipBytes`, `invalidateReaderIfMisalignedOrTooSmall`, and `readFromExistingReader`.

Control flow: `ReadAt` optionally forces a new reader, tries `readFromExistingReader`, and falls back to starting a range reader. Existing readers can be advanced by `skipBytes`, invalidated when misaligned or too small, or reused for the exact requested range. `startRead` opens either an inactive-timeout reader or a bucket read-handle reader with object generation and byte range. `readFull` spawns a cancellation goroutine when interrupts are not ignored. `readFromRangeReader` updates `start`, closes at limit, handles short reads, and discards malfunctioning readers.

State and persistence behavior: no persistent state. In-memory state tracks stream `start`, `limit`, current reader, cancel function, and reusable `readHandle`. Reads target immutable object generation metadata. NotFound during `startRead` becomes `FileClobberedError`, protecting open handles from remote deletion or generation change.

Dependencies and integration points: used by `GCSReader` for sequential/regional reads. Integrates cfg read and filesystem interrupt settings, `gcsx.NewInactiveTimeoutReader`, GCS bucket `NewReaderWithReadHandle`, metrics read capture, tracing context propagation, logger, and gcsfuse stale handle errors.

Risks: invariants must hold across all close/error paths. Cancellation goroutine must not cancel a reader after a successful read returns. `skipBytes` improves throughput but can hide read errors while discarding. Short-read handling must distinguish expected EOF at limit from premature EOF. `invalidateReaderIfMisalignedOrTooSmall` uses object size to decide whether the current stream can serve the request.

Test signals: covered through `gcs_reader_test.go` for reuse, wrong offsets, limit too small, cancellation, inactive timeout wrapping, EOF/short read, and read handle reuse; a separate range reader test file exists outside this work item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader.go -->
