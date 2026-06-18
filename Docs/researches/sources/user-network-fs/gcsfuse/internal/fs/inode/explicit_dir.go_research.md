# sources/user-network-fs/gcsfuse/internal/fs/inode/explicit_dir.go

## Purpose

`explicit_dir.go` defines the inode wrapper used when a directory is backed by an explicit GCS object or folder and therefore has a stable source generation. It bridges the general `DirInode` interface with `GenerationBackedInode`-style behavior for directory markers, enabling the parent lookup layer to preserve generation/metageneration information for explicit directories.

## Important APIs, Types, And Functions

`ExplicitDirInode` embeds `DirInode` and adds `SourceGeneration() Generation`. `NewExplicitDirInode` accepts the same construction dependencies as `NewDirInode`, plus a `*gcs.MinObject` backing object. It creates a normal directory inode via `NewDirInode`, type-asserts the returned value to `*dirInode`, wraps it in `explicitDirInode`, and copies `Generation`, `MetaGeneration`, and `Size` from the supplied min object into an inode-local `Generation`.

`explicitDirInode` embeds `*dirInode` and stores the copied `generation`. `SourceGeneration` returns that stored value. `UpdateSize` is intentionally a no-op because directory inode size is not meaningful in this filesystem model.

## Control Flow And State Behavior

Construction delegates all directory behavior to `NewDirInode`: locking, lookup count, type cache, list behavior, context, and bucket dependencies are inherited from the wrapped `dirInode`. The only extra state is the immutable-looking `generation` snapshot captured at construction. If `m` is nil, the generation remains zero-valued, which is useful for callers that need an explicit-dir wrapper but lack source object generation metadata.

The wrapper does not update its generation after construction and does not persist anything itself. Persistence remains in the remote bucket directory marker object or HNS folder. `UpdateSize` deliberately avoids mutating state, preventing generic inode size update paths from changing directory generation-size bookkeeping.

## Dependencies And Integration Points

This file depends on `cfg.Config`, `gcsx.SyncerBucket`, `gcs.MinObject`, FUSE inode attributes, `timeutil.Clock`, and a metadata prefetch semaphore. It integrates directly with `NewDirInode` and with any caller that treats explicit directory objects as `GenerationBackedInode`s for delete/rename preconditions or conflict handling.

## Risks And Test Signals

The main risk is the unchecked `wrapped.(*dirInode)` assertion, which assumes `NewDirInode` always returns that concrete type. A future abstraction around `DirInode` construction would need to update this wrapper. Another risk is stale generation data if callers expect explicit directory generation to track later remote changes. Coverage is indirect through directory tests that validate explicit directory lookup, source generations for conflict cases, and directory deletion behavior; this file has no dedicated test file in the requested subset.
