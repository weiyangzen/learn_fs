
# sources/sync-backup/kopia/tests/end_to_end_test/shallowrestore_test.go

## Purpose
Validates Kopia shallow restore semantics: placeholder files/directories, depth handling, shallow minimum-size behavior, mutation/resnapshot cycles, shallowifying safety checks, rejection of malformed placeholders, and detection of foreign repository object references.

## Important APIs, Types, And Functions
- `TestShallowrestore` snapshots a generated tree and restores it at multiple shallow depths, comparing restored placeholders against repository directory entries.
- `TestShallowrestoreWithMinSize` checks `--shallow-minsize` keeps small files real while large files become placeholders.
- `TestShallowFullCycle` applies several `filesystemmutator` operations to both a full restore and a shallow restore, snapshots the mutated shallow tree, restores it, and compares it with the mutated full tree.
- Mutators include `addOneFile`, `moveDirectory`, `moveFile`, `deepenSubtreeDirectory`, `deepenSubtreeFile`, `deepenOneSubtreeLevel`, `removeEntry`, and `addForeignSnapshotTree`.
- `TestShallowifyTree`, `TestPlaceholderAndRealFails`, and `TestForeignReposCauseErrors` cover failure cases for unsafe overwrite, malformed placeholder layouts, and invalid object IDs.
- `repoDirEntryCache` caches `snapshot.DirEntry` values fetched via `kopia show` and validates placeholder JSON through `validatePlaceholder`.
- Helper routines parse placeholder layouts through `getShallowDirEntry`, `getShallowInfo`, `findFileDir`, `findRealFileDir`, and `mustParseID`.

## Control Flow
The tests create random directory trees with files and symlinks, snapshot them, restore shallow views, then walk the original tree and compare expected restored entries. At the shallow boundary, entries should be regular placeholder files containing JSON-encoded `snapshot.DirEntry`; above the boundary entries should be real filesystem files/directories/symlinks; below the boundary entries should be absent. Mutation-cycle tests restore original data, shallow-restore the same snapshot, apply paired mutations, snapshot the shallow tree, fully restore it, and compare with the full mutated original.

## State And Persistence Behavior
Shallow restore state is represented in the filesystem using `localfs.ShallowEntrySuffix` and JSON-encoded snapshot directory entries. Repository state is read through snapshot IDs/root object IDs and `show` output. Mutators intentionally create, move, hard-link, remove, and reify files/directories so the tests verify that placeholder metadata persists through new snapshots.

## Dependencies And Integration Points
Uses `localfs`, `restore`, `snapshot`, `repo/object`, `ospath.SafeLongFilename`, `testdirtree`, `clitestutil`, and `testenv`. It integrates snapshot creation, restore, show, and local filesystem behavior, including symlink and long-name handling.

## Risks And Edge Cases
Filesystem behavior is central: path length limits, hard links, symlink timestamp precision, permissions/modes, and platform-specific path separators can affect results. Long directory names are deliberately treated as not safely suffixable. Placeholder validation is strict and can fail when `snapshot.DirEntry` schema or JSON rendering changes. The test uses deep walking and random directory structures, so failures may be noisy without careful path logs.

## Test Signals
High-value signal for shallow restore correctness, especially placeholder encoding, resnapshot fidelity, foreign object rejection, and partial reification semantics.
