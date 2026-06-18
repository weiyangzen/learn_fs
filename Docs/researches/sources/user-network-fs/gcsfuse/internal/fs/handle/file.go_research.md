<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/file.go

## Purpose

This file implements `FileHandle`, the per-open-file read-side state for gcsfuse. It coordinates reads through legacy random readers, the newer read manager, optional kernel-optimized readers, file cache or shared chunk cache, workload visualization, metrics/tracing, and inode generation consistency.

## Important APIs, Types, and Functions

`FileHandle` stores the backing `*inode.FileInode`, an invariant mutex, cached `gcsx.RandomReader`, cached `gcsx.ReadManager`, optional `kernelReader`, file cache and shared chunk cache handles, cache/read configuration, metrics/tracing handles, open mode, worker pool, global buffered-read semaphore, and a FUSE handle ID.

`NewFileHandle` registers the handle with the inode, optionally constructs a kernel reader, and initializes invariant locking. `Destroy` deregisters the handle and destroys reader resources. `ReadWithReadManager` reads through `read_manager.ReadManager`, falling back to `inode.Read` when the source generation is not authoritative. `ReadWithKernelReader` uses MRD or range-reader based kernel readers when enabled. `Read` uses `gcsx.RandomReader` for the older read path. Helpers manage lock ordering, reader/read-manager destruction, generation validation, open mode access, and direct-I/O unfinalized object size-check skipping.

## Control Flow

Read methods enter with the inode lock held and unlock it internally. They first ensure cache content if required, then choose between local inode reads and GCS-backed readers based on `SourceGenerationIsAuthoritative`. When using GCS-backed state, they release/reacquire locks via `lockHandleAndRelockInode` to preserve lock ordering, validate cached reader generation, create a new reader/read manager if stale, and perform `ReadAt`. EOF is normalized and non-EOF errors are wrapped with context. `ReadWithReadManager` can wrap the read manager in a workload insight visualizer when configured.

## State and Persistence Behavior

Reader and read-manager instances persist for the lifetime of the file handle as long as their object generation matches the inode's source generation; size is refreshed on valid reuse. Destroy tears them down and deregisters read/write handle counts from the inode. File cache/chunk cache state is external. The workload visualization path may create its configured output file.

## Dependencies and Integration Points

This file sits between FUSE file operations and `inode.FileInode`, `internal/gcsx`, `kernel_readers`, `read_manager`, file cache, workerpool, metrics, tracing, and workload insight. It depends on `cfg.Config` for feature flags, `util.OpenMode` for access/direct flags, and semaphores for buffered-read block limits.

## Risks and Edge Cases

Lock order is a major risk: read paths must avoid deadlocks between inode locks and handle locks. Generation mismatch must destroy stale readers to avoid reading clobbered content. Cache-content mode intentionally forces inode fallback. Kernel reader must be initialized only when enabled. `shouldSkipSizeChecks` assumes `readManager` is non-nil and is only valid after manager creation; it is limited to rapid-write bucket types, direct I/O, unfinalized objects, and reads extending past known size.

## Test Signals

The paired tests cover read/read-manager success, concurrent reads, EOF and wrapped errors, fallback to inode content, generation-change invalidation, kernel-reader zonal vs standard behavior, lock-order deadlock scenarios, destroy/invariant calls, open mode preservation, buffered full and concurrent reads, direct-I/O size-check conditions, and workload insight file creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file.go -->
