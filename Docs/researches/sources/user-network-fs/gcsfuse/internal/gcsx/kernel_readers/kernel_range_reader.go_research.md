## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader.go

Purpose: implements a kernel-optimized range reader for standard/regional buckets, creating a fresh GCS range reader for every request.

Important APIs/types/functions: `KernelRangeReader`, `NewKernelRangeReader`, `CheckInvariants`, `ReadAt`, `Destroy`, and `ReaderName`.

Control flow: `CheckInvariants` panics if bucket or instance is nil. `ReadAt` fetches the current `MinObject` from `KernelRangeReaderInstance`, returns an error if nil, returns EOF for offsets at/after object size, caps end offset at object size, opens a reader with `NewReaderWithReadHandle`, `io.ReadFull`s the exact bounded slice, defers close with warning on close error, and captures parallel read metrics.

State/persistence behavior: stateless aside from bucket, instance, and metrics. It reads remote data but does not cache or persist local state. Current object generation/size come from the shared instance, allowing updates after sync or mutation.

Dependencies/integration: depends on `gcsx.Reader`, GCS byte ranges, storage reader close semantics, logger, and metrics. It is selected by `NewKernelReader` for non-rapid buckets.

Risks/test signals: every read creates a new connection, trading simplicity for per-read overhead. Partial reads return `io.ErrUnexpectedEOF` from `io.ReadFull` if the storage reader under-delivers. Tests cover success, EOF, partial object-size capping, new-reader errors, nil object, name, and constructor.
