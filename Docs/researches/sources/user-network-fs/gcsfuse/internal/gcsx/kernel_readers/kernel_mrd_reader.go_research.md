## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader.go

Purpose: implements a kernel-optimized reader for rapid/zonal buckets using a shared `gcsx.MrdInstance` and multi-range downloader pool.

Important APIs/types/functions: `KernelMRDReader`, `NewKernelMRDReader`, `isShortRead`, `ReaderName`, `CheckInvariants`, `ReadAt`, and `Destroy`. State includes an atomic flag tracking whether the MrdInstance refcount has been incremented, the instance pointer, and metrics handle.

Control flow: empty buffers return immediately. First real read increments the MrdInstance refcount exactly once. Reads delegate to `MrdInstance.Read`, capture parallel GCS read metrics, and retry when `isShortRead` sees bytes fewer than requested plus a gRPC `OutOfRange` error. Retry recreates the MRD pool if possible, then reads the remaining buffer from the advanced offset. `Destroy` decrements refcount if in use and nils the instance.

State/persistence behavior: does not store data; manages MrdInstance lifecycle through refcount. Short-read recovery updates remote connection state by recreating MRD, not object metadata.

Dependencies/integration: integrates with `gcsx.Reader`, `MrdInstance`, metrics, gRPC status/codes, and logger. It is selected by `NewKernelReader` for rapid buckets.

Risks/test signals: assumes `Destroy` only runs after active reads finish. If MRD recreation fails, retry continues with the older MRD. Tests cover empty/nil/success/multiple reads, short-read classification, retry behavior, destroy refcounting, and context cancellation.
