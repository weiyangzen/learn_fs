# Research: sources/object-store/minio-mc/cmd/parallel-manager.go

## sources/object-store/minio-mc/cmd/parallel-manager.go

Purpose: provides adaptive concurrent task execution for copy/mirror style workloads while considering bandwidth improvement and memory pressure.

Important APIs and types: `task` wraps a `func() URLs`, barrier flag, and upload size. `ParallelManager` owns worker count, queue/result channels, wait group, barrier lock, byte counter, max memory, and max worker cap. Key methods are `addWorker`, `Read`, `monitorProgress`, `queueTask`, `queueTaskWithBarrier`, `enoughMemForUpload`, `doQueueTask`, `stopAndWait`, and constructor `newParallelManager`.

Control flow: construction starts `runtime.NumCPU()` workers and a monitor goroutine. Tasks are queued under a read lock or exclusive lock for barriers. Workers execute tasks and send `URLs` to the result channel. The monitor samples bytes every four seconds and adds workers while bandwidth improves, up to `maxWorkers` or 128.

State and persistence: no persistent storage; process state includes goroutines and atomics. `Read` acts as a progress counter for readers that tee through the manager.

Dependencies and integration: used by mirror and likely copy status paths. It calls MinIO `OptimalPartInfo`, `gopsutil/mem`, cgroup memory limit files, and Go runtime GC/memstats.

Risks and tests: `for range defaultWorkerFactor` requires modern Go integer range syntax. Barrier tasks block queuing until running work finishes. Memory estimates panic on unexpected inputs or `OptimalPartInfo` errors. No direct tests cover concurrency behavior.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/parallel-manager.go -->
