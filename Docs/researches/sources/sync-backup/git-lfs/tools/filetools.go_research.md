# sources/sync-backup/git-lfs/tools/filetools.go

Purpose: core file/path helpers for Git LFS tools, including existence checks, permission-aware directory and temp-file creation, tilde/config expansion, hash verification, concurrent directory walking, write-bit toggling, executable permission derivation, and canonical path handling.

Important APIs/types/functions: `FileOrDirExists`, `FileExists`, `DirExists`, `FileExistsOfSize`, `ResolveSymlinks`, `RenameFileCopyPermissions`, `CleanPaths`, `repositoryPermissionFetcher`, `Mkdir`, `MkdirAll`, `ExpandPath`, `ExpandConfigPath`, `VerifyFileHash`, `FastWalkDir`, `fastWalker`, `SetFileWriteFlag`, `TempFile`, `ExecutablePermissions`, `CanonicalizePath`, and `TrimCurrentPrefix`. Test seams are the package-level `currentUser`, `lookupUser`, and `lookupConfigHome` function variables.

Control flow: simple path helpers delegate to `os.Stat`; rename first mirrors destination permissions onto the source then calls `RobustRename`; path expansion parses `~`/`~user`, consults injected user lookup functions, optionally resolves symlinks, and joins the suffix. `FastWalkDir` starts a goroutine-backed walker, reads directory entries in batches of 100, and uses a configurable goroutine limit from `LFS_FASTWALK_LIMIT`. `CanonicalizePath` first translates Cygwin paths, makes them absolute, then calls the platform-specific canonicalizer, allowing missing paths only when requested.

State and persistence: no durable state is owned here, but file modes, temp files, destination replacement, and filesystem traversal are direct side effects. `TempFile` creates real temp files with repository permissions and cleans up on chmod failure. Fast walk state is held in channels, wait groups, and atomic counters until traversal completes.

Dependencies and integration points: depends on Go `os`, `filepath`, `runtime`, `sync/atomic`; Git LFS `errors` and `tr`; platform files provide `CanonicalizeSystemPath`, `RobustRename`, and `doWithUmask`. Integrates with repository configuration through `RepositoryPermissions`, with transfer code through hash verification and temp-file helpers, and with Cygwin handling in `os_tools.go`.

Risks: `FastWalkDir` is intentionally unordered, so callers must not depend on sorted traversal. The global umask change in `Mkdir`/`MkdirAll` is process-wide during the callback. `CleanPaths` trims separators but does not call `path.Clean` despite the comment. `ExpandPath` relies on package globals that tests mutate. `VerifyFileHash` reads whole files and reports mismatches only after full copy.

Test signals: `filetools_test.go` covers clean paths, tilde/config expansion, fast walking with large directories, write-flag behavior across platforms, and executable permission mapping.
