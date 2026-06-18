# sources/user-network-fs/rclone/fs/walk/walk.go

## Purpose
This package implements directory traversal and recursive listing helpers for rclone filesystems. It chooses between concurrent non-recursive `List` traversal and backend `ListR`, applies filters, handles max-depth behavior, synthesizes directories for bucket-style remotes, and can materialize listings as `dirtree.DirTree`.

## Important APIs, Flow, and State
`ErrorSkipDir` lets a walk callback skip a directory. `ErrorCantListR` reports unavailable recursive listing. `Walk` is the main ordered traversal API. `ListType` (`ListObjects`, `ListDirs`, `ListAll`) filters recursive listing entries. `ListR` uses backend `Features().ListR` when safe, otherwise falls back to walking. `GetAll` collects recursive objects and directories. Internal helpers include `dirMap`, `listR`, `walk`, `walkRDirTree`, `walkNDirTree`, `NewDirTree`, and `walkR`.

`Walk` adjusts filter-aware backend behavior, then chooses no-traverse/files-from, `ListR`, or sorted `List` paths. The non-recursive `walk` path starts `ci.Checkers` workers, serializes callback calls with a mutex, tracks outstanding jobs, and returns the first counted error. Direct `listR` counts listed entries, optionally synthesizes missing parents, filters entry kinds, applies active filters, and serializes callbacks. `walkRDirTree` converts arbitrary-order recursive entries into a sorted tree with parent synthesis, depth clipping, excluded-object parent preservation, and exclude-file pruning.

## Dependencies, Risks, and Test Signals
Dependencies include `fs`, `accounting`, `dirtree`, `filter`, and `list`. The package is used by sync, operations, fstest cleanup/listing, and recursive enumeration callers. Risks are concurrency, callback ordering, depth semantics, filter-aware backend behavior, no-traverse/files-from handling, bucket directory synthesis, and error counting. `walk_test.go` covers these paths with mock entries and golden tree output.
