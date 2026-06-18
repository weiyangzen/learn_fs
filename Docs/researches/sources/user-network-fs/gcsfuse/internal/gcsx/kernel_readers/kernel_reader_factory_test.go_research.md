## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory_test.go

Purpose: verifies `NewKernelReader` dispatches to the expected concrete reader for rapid versus standard buckets.

Important APIs and fixtures: two tests create a `storage.TestifyMockBucket`, configure `BucketType`, call `NewKernelReader`, and assert returned concrete type.

Control flow and behavior covered: `TestNewKernelReader_Zonal` expects `*KernelMRDReader` when `BucketType{Zonal: true}`. `TestNewKernelReader_Standard` expects `*KernelRangeReader` when `Zonal` is false.

State/persistence signals: no persistence. Tests validate factory wiring only.

Dependencies/integration: uses mock bucket and `gcs.BucketType`. It intentionally passes nil reader instances/metrics because construction, not read behavior, is under test.

Risks/test signals: narrow but high-signal coverage for branch selection. It does not check other `BucketType` fields beyond `Zonal`/rapid behavior.
