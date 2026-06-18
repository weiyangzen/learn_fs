# sources/user-network-fs/rclone/lib/dircache/dircache.go

## Purpose
`dircache.go` implements rclone's directory path-to-ID cache for backends whose directories have opaque IDs. It maps relative paths to IDs and IDs back to paths, discovers or creates missing parent directories, and helps prepare safe directory moves.

## Important APIs, types, and functions
- `DirCache` stores forward/inverse maps plus root state: true root ID, configured root path, current root ID, root parent ID, and whether the configured root has been found.
- `DirCacher` is the backend interface: `FindLeaf(ctx, parentID, leaf)` and `CreateDir(ctx, parentID, leaf)`.
- Basic cache methods include `Get`, `GetInv`, `Put`, `Flush`, `FlushDir`, `String`, and `SetRootIDAlias`.
- Path/root methods include `SplitPath`, `FindDir`, `_findDir`, `FindPath`, `FindRoot`, `_findRoot`, `FoundRoot`, `RootID`, `RootParentID`, and `ResetRoot`.
- `DirMove` performs preflight lookup and directory creation for a backend directory move.

## Control flow
`New` initializes empty maps and resets the root to the true root ID. `FindDir` takes the root-state mutex, ensures `FindRoot` has run, and recursively resolves each path component with `_findDir`. `_findDir` returns cached IDs when possible, otherwise resolves the parent, calls backend `FindLeaf`, optionally calls `CreateDir`, and caches the result. `_findRoot` resolves the configured root from the true root, records its parent ID, flushes the old tree, and re-roots the cache so `""` maps to the configured root ID. `RootParentID` can resolve the parent without creating the root itself. `DirMove` refuses root moves, creates destination parents, verifies destination absence, then resolves source parent and source ID.

## State and persistence behavior
The cache is purely in-memory; backend `CreateDir` and actual move operations persist remote state. `cacheMu` protects map access, while `mu` serializes root discovery and recursive backend lookups. `ResetRoot` clears cached paths and restores the absolute root mapping.

## Dependencies and integration points
The package depends on `context`, `path`, `strings`, `sync`, and rclone `fs` errors such as `ErrorDirNotFound` and `ErrorDirExists`. It is used by ID-based backends including cloud storage remotes to translate rclone paths into backend directory IDs.

## Risks and edge cases
Duplicate names in a backend can make path-to-ID mappings ambiguous; backends must define `FindLeaf` behavior. `SetRootIDAlias` intentionally avoids locking because it is called from backend `FindLeaf`, so misuse outside that path can race. `FlushDir` removes entries by string prefix and assumes slash-separated normalized paths. `RootParentID` returns errors for true-root cases. `DirMove` only prepares IDs; callers must flush source cache after performing the remote move.

## Test signals
No tests for `dircache` are in this subset, but many backend integration tests exercise it indirectly. Important missing direct signals include concurrent lookup behavior, duplicate-name handling, root aliasing, and `DirMove` cache invalidation.
