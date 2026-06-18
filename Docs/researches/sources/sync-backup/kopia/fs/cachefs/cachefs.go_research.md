<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cachefs.go -->
# sources/sync-backup/kopia/fs/cachefs/cachefs.go

## Purpose
Defines wrapper entry types that add directory-entry caching behavior around existing `fs.Entry` implementations.

## Important APIs, Types, And Functions
Key symbols are `DirectoryCacher`, `cacheContext`, wrapper structs `directory`, `file`, `symlink`, `Wrap`, and `wrapWithContext`. Compile-time assertions ensure wrappers implement fs interfaces.

## Control Flow
`Wrap` creates a shared cache context. Directories override `Child` and `IterateEntries` to wrap returned children with the same context and delegate iteration to the cacher. Files and symlinks embed underlying interfaces without behavior changes but carry the context for type consistency.

## State And Persistence Behavior
No persistent state exists; wrappers hold pointers to the cache context and underlying entries. Cached directory data is owned by the provided `DirectoryCacher`.

## Dependencies And Integration Points
Integrates the `fs` package interfaces and `Cache.IterateEntries` from `cache.go`.

## Risks And Edge Cases
Wrapping preserves only Directory/File/Symlink type categories; entries implementing multiple extra interfaces may lose direct type assertions unless embedded interface exposes them. The cacher must be non-nil for directory iteration.

## Test Signals
Tests should cover Child and IterateEntries wrapping, nested directory reuse of context, and preservation of file/symlink behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/cachefs/cachefs.go -->
