# sources/user-network-fs/gcsfuse/internal/fs/inode/recursive_cancellation_test.go

Purpose: verifies that cancelling prefetch work at a directory inode propagates to child and grandchild directory contexts. This protects metadata prefetch behavior from leaking goroutines or continuing recursive work after a parent directory is invalidated or torn down.

Important APIs and helpers: the `RecursiveCancellationTest` suite builds a fake GCS bucket, wraps it in `gcsx.NewSyncerBucket`, and prepares a `cfg.Config` with metadata prefetch enabled and metadata cache sizes/TTL set. `createDirInode` calls `NewDirInode` with a parent context, standard directory attributes, implicit directories enabled, a one-minute TTL, a weighted semaphore, and the suite config, then casts the result to `*dirInode` so it can inspect private `Context()` and cancellation behavior.

Control flow and state: `SetupTest` initializes a simulated clock, fake bucket, syncer bucket, and config. `TestRecursiveCancellation` creates a root dir with no parent context, a child using `rootDir.Context()`, and a grandchild using `childDir.Context()`. It first asserts all contexts are active, then calls `rootDir.CancelSubdirectoryPrefetches()` and expects `context.Canceled` on all three contexts.

Dependencies and integration: this is an internal package test, so it reaches `dirInode` internals. It integrates with `cfg`, `gcsx`, fake storage, `fuseops`, `timeutil`, and `golang.org/x/sync/semaphore`. It is coupled to the directory inode context tree used by metadata prefetch.

Risks: the test only exercises a simple linear tree and does not start actual prefetch goroutines or validate semaphore release. It assumes `NewDirInode` returns `*dirInode` for this configuration. It also uses repeated `NewDirName(..., "child/")` style inputs, relying on constructor behavior that accepts already slash-terminated directory names.

Test signals: failures indicate broken recursive cancellation propagation, a changed context-parenting model, or cancellation no longer reaching descendants.
