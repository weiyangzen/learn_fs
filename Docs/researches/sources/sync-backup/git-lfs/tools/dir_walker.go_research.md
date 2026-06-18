<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/dir_walker.go -->
# sources/sync-backup/git-lfs/tools/dir_walker.go

Purpose: walks and optionally creates directory prefixes for Git-provided relative file paths, validating that each path segment is a directory.

Important APIs/types/functions: errors `errInvalidDir` and `errNotDir`, `DirWalker`, `NewDirWalkerForFile`, `walk`, `Walk`, and `WalkAndCreate`.

Control flow: `NewDirWalkerForFile` strips the filename from a slash-separated Git path, leaving only directory components. `walk` iterates path segments from `parentPath`, rejects empty, `.`, or `..` segments, stats each joined path, returns not-exist when missing and create is false, calls `Mkdir` when create is true, errors if an existing component is not a directory, and updates `parentPath`/`path` as it progresses. `Walk` checks only; `WalkAndCreate` creates missing directories.

State and persistence: mutates the `DirWalker` fields to track the deepest existing/created parent and remaining missing path. `WalkAndCreate` persists directories on disk using repository permissions.

Dependencies and integration points: depends on Git LFS `errors`, translation `tr`, `Mkdir`, and `repositoryPermissionFetcher`. Used wherever Git LFS must prepare working-tree directories safely for checkout/smudge operations.

Risks: intentionally does not guard TOCTOU races, matching Git-style behavior. It assumes Git-normalized relative paths; invalid paths are rejected but absolute/empty/trailing slash inputs have edge cases tested.

Test signals: `dir_walker_test.go` covers path derivation, existing/missing/created dirs, files and symlink conflicts, trailing slashes, invalid segments, and parent-path variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/dir_walker.go -->
