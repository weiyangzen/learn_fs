## sources/user-network-fs/go-fuse/fs/rmchild_test.go

Purpose: concurrency stress test for `Inode.RmChild` and child-map mutation.

Important APIs/types/functions: `TestRmChildParallel` creates many named persistent child inodes, starts goroutines that remove children concurrently, and validates operations complete without races or panics.

Control flow: per iteration, root is populated, goroutines call `RmChild` over different names, and a wait group joins. The test repeats to increase exposure to scheduling variance.

State and persistence: only the in-memory inode child map is mutated. Removed child references are transient.

Dependencies and integration: targets `fs.Inode` locking and tree bookkeeping used by lookup, unlink, rename, and notification paths.

Risks and test signals: catches missing locks, map concurrent writes, and stale parent/child relationships. It is most valuable under `go test -race`.
