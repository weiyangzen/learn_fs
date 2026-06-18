# sources/sync-backup/syncthing/lib/fs/walkfs.go

## Purpose
Implements deterministic recursive filesystem walking with root-relative paths and optional infinite-recursion detection for Windows junction traversal.

## Important APIs, Types, and Functions
`ErrInfiniteRecursion`, `ancestorDirList`, `WalkFunc`, `walkFilesystem`, `NewWalkFilesystem`, `walk`, `Walk`, and `underlying`.

## Control Flow
`Walk` lstats the root, then recursively calls `walk`. Each path is canonicalized, passed to the callback, and skipped/stopped based on callback errors. Directories list names with `DirNames`, lstat children, and recurse in directory listing order. When `OptionJunctionsAsDirs` is present, ancestor `SameFile` checks detect recursion and call the callback with `ErrInfiniteRecursion`.

## State and Persistence Behavior
No persistent state. Runtime stack tracks ancestor directory `FileInfo` values for recursion detection.

## Dependencies and Integration Points
Always applied by `NewFilesystem`. Relies on underlying `Lstat`, `DirNames`, `SameFile`, and options.

## Risks
Directory names are documented as lexical but this code does not sort `DirNames`; deterministic order depends on underlying implementations returning sorted names. `SkipDir` behavior follows Go filepath semantics. Recursion detection quality depends on `SameFile`.

## Test Signals
`walkfs_test.go` covers symlink skipping, Windows junction traversal, and infinite recursion detection.
