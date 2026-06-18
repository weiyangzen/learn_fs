# sources/sync-backup/restic/internal/archiver/tree.go

Purpose: Builds and normalizes the virtual tree that maps user backup targets into snapshot paths. It handles relative paths, absolute roots, Windows volumes, duplicate target elimination, root-name collisions, and target unrolling.

Important APIs and types: `tree` stores child `Nodes`, leaf `Path`, `FileInfoPath`, `Root`, and `Explicit`. `pathComponents`, `rootDirectory`, `tree.Add`, `tree.add`, `Leaf`, `NodeNames`, `formatTree`, `unrollTree`, `backupTarget`, and `newTree` implement the mapping.

Control flow and state: `newTree` cleans each target, skips duplicates, calls `Add`, then `unrollTree`. `Add` converts the path into components, determines the root, resolves top-level name collisions by suffixing names such as `foo-1`, and marks direct leaf targets as explicit. `unrollTree` expands a node that is both a leaf and a parent by reading its directory contents so that only leaves retain `Path`.

Persistence and dependencies: The tree is in-memory. The only filesystem reads occur during `unrollTree` via `fs.Readdirnames`. Dependencies include `fs.FS`, sorted names, `debug`, and restic errors.

Integration points: Both archiver snapshot saving and scanner traversal use this representation. `Explicit` is consumed by scanner/save logic to bypass filters only for user-listed target paths.

Risks and test signals: Risks include unstable snapshot shape, path collision bugs, duplicate handling, relative-parent targets, Windows volume roots, and filters applied to the wrong target. `tree_test.go` and `archiver_test.go` provide extensive coverage.
