<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/file_test.go

## Purpose

This testify suite validates `FileHandle` behavior across random-reader, read-manager, kernel-reader, buffered-read, lock-order, lifecycle, open-mode, and workload-insight paths. It uses fake buckets and real file inodes to exercise the handle close to production control flow.

## Important APIs, Types, and Functions

`fileTest` owns a context, simulated clock, and syncer bucket. `createDirInode` constructs a parent directory inode. `createFileInode` creates a fake GCS object and corresponding `inode.FileInode`. The suite uses `read_manager.MockReadManager`, `gcsx.MockRandomReader`, `storage.TestifyMockBucket`, fake multi-range downloaders, worker pools, and semaphores.

Named tests cover reader validity, read success and concurrency, error paths, inode fallback, generation invalidation, kernel reader success/failures, open mode, destroy and invariants, lock helpers, buffered reads, size-check skipping, and workload visualization.

## Control Flow

Most tests build an inode and file handle, manually take the inode lock as required by production method contracts, call the target `FileHandle` method, and then assert data, errors, internal reader state, or mock expectations. Concurrency tests spawn multiple goroutines reading random ranges through a shared file handle and use timeouts to detect deadlocks. Kernel-reader tests branch between zonal MRD and standard range-reader behavior via bucket type.

## State and Persistence Behavior

Fake bucket objects hold test content and generations. File handles cache readers/read managers across calls. Some tests write and sync the inode to change GCS generation, proving stale cached readers are replaced. Workload insight writes `test.txt` and removes it after validation. Worker pools are stopped with defer.

## Dependencies and Integration Points

The suite integrates `inode.FileInode`, `gcsx.SyncerBucket`, fake storage buckets, content cache, read manager, kernel reader dependencies, workerpool, metrics/tracing noops, FUSE handle IDs, semaphores, and `util.OpenMode`. It validates contracts assumed by higher-level FUSE file operation handlers.

## Risks and Edge Cases

The tests are intentionally close to internal locking contracts; incorrect lock ownership can deadlock or panic. Mock-based error tests depend on exact method calls. `shouldSkipSizeChecks` has a panic case for nil read manager but the table currently does not activate it. Concurrency tests use random offsets and timeouts, which can reveal races but may be timing-sensitive.

## Test Signals

Signals include byte-for-byte read data, response sizes, EOF propagation, wrapped error matching, stale reader replacement after generation changes, MRD/range-reader invocation, explicit nil kernel-reader error, no deadlocks under lock contention, open-mode round trips, buffered-read reconstruction, rapid-write direct-I/O skip decisions, and workload insight output file existence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file_test.go -->
