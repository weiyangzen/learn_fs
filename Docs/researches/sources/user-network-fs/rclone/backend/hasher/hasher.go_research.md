# sources/user-network-fs/rclone/backend/hasher/hasher.go

## Purpose
This file implements the main filesystem wrapper for the hasher backend. Hasher wraps another rclone remote and augments its hash capabilities by passing through fast native hashes, caching slow native hashes, and computing configured hashes locally when needed.

## Important APIs, Types, And Control Flow
`init` registers the `hasher` remote with `remote`, `hashes`, `max_age`, and `auto_size` options plus backend command help. `Options` captures those settings. `Fs` embeds the wrapped `fs.Fs` and stores wrapper metadata, kv DB handle, fingerprint strategy, and hash sets grouped as passed, slow, auto, keep, and supported.

`NewFs` rejects unsupported OSes and self-wrapping, derives the wrapped remote using `fspath.JoinRootPath` and `cache.Get`, adjusts root for file remotes, classifies underlying hashes based on `SlowHash`, parses configured hashes, starts the kv DB when `max_age > 0`, builds a feature mask from the base remote, enables `ListP`, and pins the base remote until finalization.

Most filesystem methods delegate to the underlying remote while preserving hasher wrapping and cache state. `wrapEntries`, `List`, `ListP`, and `ListR` wrap objects in hasher `Object`. `Purge`, `PutStream`, `PutUnchecked`, `Move`, and `DirMove` prune or move cached records around underlying operations. `Copy` delegates and wraps. Optional operations such as `CleanUp`, `About`, `ChangeNotify`, `UserInfo`, `Disconnect`, `MergeDirs`, `DirSetModTime`, `MkdirMetadata`, `DirCacheFlush`, and `PublicLink` pass through when available. `Shutdown` stops the kv DB and then the underlying remote. Object wrapper methods expose the hasher `Fs`, underlying object via `UnWrap`, and optional ID/tier/mime/metadata behavior.

## State And Persistence
Runtime state tracks the wrapped remote, optional wrapper parent, feature mask, and hash classification. Persistent state is the kv database created by `kv.Start(ctx, "hasher", f.Fs)` when caching is enabled. Cache records are pruned on overwrites/removes elsewhere, purged for directories, and migrated on moves. With `max_age=0`, the DB is disabled and caching paths must handle inactive DB behavior.

## Dependencies And Integration Points
The file integrates rclone's wrapper interfaces, feature masking, `cache.Get`, `kv`, `list.WithListP`, and hash/type parsing. Hash calculation, raw get/put, object update/remove/open, and fingerprint details are implemented in adjacent hasher package files; this file provides the wrapper and lifecycle surface they depend on.

## Risks And Test Signals
Risks include nil DB use in cache maintenance paths when `max_age=0`, feature masks advertising behavior incorrectly after wrapping, root/path mismatches when the wrapped remote points to a file, hash classification errors for slow or unsupported hashes, and cache records becoming stale after delegated operations not covered by pruning/move logic. Tests should exercise wrapping around local and nonlocal remotes, disabled cache mode, slow-hash remotes, server-side move/copy/dir-move, purge, shutdown idempotence, and optional interface passthrough.
