## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_instance.go

Purpose: provides a small thread-safe holder for the latest `gcs.MinObject` used by `KernelRangeReader`.

Important APIs/types/functions: `KernelRangeReaderInstance`, `NewKernelRangeReaderInstance`, `SetMinObject`, and `GetMinObject`.

Control flow: construction stores the initial object. `SetMinObject` takes a write lock and replaces the pointer. `GetMinObject` takes a read lock and returns the stored pointer.

State/persistence behavior: state is in memory only and represents current object metadata such as name, generation, size, and content encoding. There is no copy-on-read despite the comment saying “copy”; callers receive the pointer currently held.

Dependencies/integration: depends only on `sync.RWMutex` and `gcs.MinObject`. Used by kernel range readers and factory wiring for standard buckets.

Risks/test signals: pointer return means callers could mutate the object without locking if they hold the pointer. No dedicated test file is listed for this instance; factory and range-reader tests indirectly exercise it.
