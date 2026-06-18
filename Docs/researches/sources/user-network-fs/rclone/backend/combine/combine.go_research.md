# sources/user-network-fs/rclone/backend/combine/combine.go

## Purpose
This file implements the `combine` backend, which overlays multiple configured upstream remotes under top-level directory mountpoints. It presents them as one directory tree while delegating most operations to the appropriate upstream backend after translating paths.

## Important APIs, types, and functions
`Options` contains the space-separated `upstreams` config. `Fs` stores backend identity, root, common hash set, synthetic directory timestamp, feature set, and a map of mountpoint names to `upstream` values. `adjustment` maps paths between upstream-relative and combined-root-relative namespaces through `do` and `undo`. `upstream` wraps an `fs.Fs`, its mountpoint directory, and path adjustment. `NewFs` parses and validates upstream definitions, creates upstream filesystems concurrently through `cache.Get`, pins them until finalized, constructs a feature mask over all upstreams, and detects file roots.

Core APIs include `findUpstream`, `multithread`, `ListP`, `ListR`, `NewObject`, `Put`, `PutStream`, `Copy`, `Move`, `DirMove`, `Purge`, `About`, `ChangeNotify`, metadata and tier delegation, `PublicLink`, `MergeDirs`, and object wrappers.

## Control flow
Operations first resolve the combined path to an upstream with `findUpstream`. Root listing with empty root emits synthetic top-level directories for each upstream. Non-root listing delegates to upstream `ListP` or `List`, then wraps returned objects/directories so their `Remote()` values appear under the combined namespace. Recursive root listing lists synthetic upstream directories first, then recursively lists each upstream in parallel with a mutex-protected callback. Writes either update existing combined objects or delegate puts to the resolved upstream using `fs.NewOverrideRemote`.

Server-side operations are intentionally limited to same-combine objects. `Copy` and `Move` unwrap `*combine.Object`, locate destination upstreams, use destination `Copy`/`Move` if available, and wrap the returned object. `Move` falls back to copy plus source removal when move is unavailable but copy exists. Directory moves require both source and destination paths to resolve and delegate to destination upstream `DirMove`.

## State and persistence behavior
The combine backend stores no file data itself. Persistent data remains in upstream remotes. Local state includes upstream mappings, feature decisions, common hash intersection, and a synthetic `when` timestamp for top-level mounted directories. Root directories are virtual: `Mkdir` and `Rmdir` at empty root succeed without touching upstreams. `Purge` at empty root purges all upstream roots in parallel.

## Dependencies and integration points
The file is deeply integrated with rclone `fs`, `cache`, `operations`, `list`, `walk`, and `hash` packages. Feature masking controls the surface exposed by the wrapper, while selected optional features are re-enabled if any or all upstreams can support them. It marks `features.Overlay = true` and advertises metadata support inherited from upstreams.

## Risks and edge cases
Upstream mountpoint dirs cannot contain `/`, so this backend only supports one-level mount roots. Map iteration order means upstream resolution order is nondeterministic; overlapping path adjustments are mostly prevented by mountpoint restrictions, but root and file-root behavior still deserves care. `PutUnchecked` returns the underlying object without wrapping it, unlike `Put`, which may leak the upstream namespace to callers. Feature selection is conservative in most places, but `ListR` enables fallbacks based on ListR/local combinations and should be tested across mixed remotes. Cross-upstream `Move` may use destination copy on an object from another upstream; whether that succeeds depends on the destination backend's server-side copy constraints.

## Test signals
`combine_internal_test.go` unit-tests path adjustment. `combine_test.go` runs generic `fstests` against local, memory, mixed local/memory, or an externally configured remote. These tests provide broad filesystem behavior coverage but limited direct assertions for feature masking, change notifications, quota aggregation, and cross-upstream server-side operations.
