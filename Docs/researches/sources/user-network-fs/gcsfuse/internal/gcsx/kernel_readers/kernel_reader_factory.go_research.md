## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory.go

Purpose: chooses the kernel-optimized reader implementation based on bucket type.

Important API: `NewKernelReader(bucket, kernelRangeReaderInstance, mrdInstance, metricsHandle) gcsx.Reader`.

Control flow: calls `bucket.BucketType().IsRapid()`. Rapid/zonal buckets receive `NewKernelMRDReader(mrdInstance, metricsHandle)` for MRD-backed parallel reads. Other buckets receive `NewKernelRangeReader(bucket, kernelRangeReaderInstance, metricsHandle)` for per-request range reads.

State/persistence behavior: the factory owns no persistent state and simply wires the correct reader with shared instances supplied by higher layers.

Dependencies/integration: integrates `gcs.BucketType`, `gcsx.MrdInstance`, `KernelRangeReaderInstance`, metrics, and the `gcsx.Reader` interface. It is the selection point that aligns kernel read path with storage backend capabilities.

Risks/test signals: if bucket type classification changes, this factory controls behavior. It does not validate nil arguments; selected reader may error/panic later depending on use. Tests cover rapid and standard selection.
