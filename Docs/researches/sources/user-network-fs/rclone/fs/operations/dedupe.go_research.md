# sources/user-network-fs/rclone/fs/operations/dedupe.go

## Purpose
`dedupe.go` resolves duplicate file names or duplicate hashes on backends that can expose multiple objects at the same path, and can also merge duplicate directories before file deduplication.

## Important APIs, types, and functions
- `dedupeRename` renames duplicate files to numbered suffixes without colliding with existing names.
- `dedupeDeleteAllButOne` deletes all duplicate objects except a selected index.
- `dedupeDeleteIdentical` removes duplicates that share size or hash, while avoiding duplicate object IDs that appear multiple times in listings.
- `dedupeList` and `dedupeInteractive` print duplicate choices and optionally prompt the user.
- `DeduplicateMode` is the pflag-compatible mode enum with `Set`, `String`, and `Type`.
- `dedupeDir`, `dedupeDirsMap`, `dedupeFindDuplicateDirs`, and `dedupeMergeDuplicateDirs` detect duplicate directories and call backend `MergeDirs`.
- `Deduplicate` is the exported orchestration function.

## Control flow
`Deduplicate` selects a backend hash when needed, logs the duplicate criterion, optionally scans and merges duplicate directories for name-based dedupe, then lists all objects recursively. It groups objects either by remote path or by hash. For each duplicate group, name-based dedupe first removes identical copies where possible, then applies the requested mode: interactive, first, newest, oldest, rename, largest, smallest, skip, or list.

Directory dedupe walks all entries, builds directory nodes keyed by backend IDs when available, tracks parent relationships and recursive child counts, sorts duplicate directory names parent-first, and merges each duplicate set with the largest subtree first to minimize movement.

## State and persistence behavior
This file performs destructive remote mutations: object deletion, server-side object moves, and directory merges. It respects `SkipDestructive` before renames and directory merges, while `DeleteFile` handles its own destructive checks. It does not persist local state beyond in-memory grouping maps.

## Dependencies and integration points
It uses `fs.Features().Move`, `PutUnchecked`, `MergeDirs`, and `DirCacheFlush`; `fs.IDer` and `fs.ParentIDer`; `walk.ListR`; `operations.DeleteFile`; `accounting` checking transfers; `config.Command`; and hash support from `fs/hash`. It is the implementation behind the rclone dedupe command.

## Risks and edge cases
Backends can report the same object ID multiple times; deleting those would risk data loss, so repeated IDs are ignored. Hashless backends fall back to size-only behavior only when configured. Rename mode must avoid existing `name-N.ext` collisions and gives up after many attempts. Directory merging depends on backend support and cache flushing. Interactive mode can terminate the whole dedupe pass.

## Test signals
`dedupe_test.go` covers pflag compatibility, interactive/default behavior, skip, size-only duplicate deletion, first/newest/oldest/largest/smallest selection, by-hash dedupe, rename collision avoidance, and `MergeDirs` behavior.
