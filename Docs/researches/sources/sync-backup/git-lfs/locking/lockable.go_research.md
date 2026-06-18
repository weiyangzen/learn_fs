# sources/sync-backup/git-lfs/locking/lockable.go

Purpose: Manages `.gitattributes` lockable patterns and filesystem write flags for lockable files.

Important APIs/types/functions: `GetLockablePatterns`, `getLockableFilter`, `ensureLockablesLoaded`, `refreshLockablePatterns`, `IsFileLockable`, `FixAllLockableFileWriteFlags`, `FixFileWriteFlagsInDir`, `fixFileWriteFlags`, `FixLockableFileWriteFlags`, and `fixSingleFileWriteFlags`.

Control flow: Lockable patterns are lazily loaded under mutex from Git attributes. File write-flag fixers build filters for lockable/unlockable patterns, enumerate tracked files with `git.NewLsFiles`, and call `tools.SetFileWriteFlag` based on whether a file is lockable and locked by the current committer.

State and persistence behavior: Caches lockable patterns and filter on `Client`. Mutates filesystem permissions by setting files read-only or writable. Reads Git attributes and Git index/tracked-file state.

Dependencies and integration points: Integrates `gitattr`, `filepathfilter`, `git.NewLsFiles`, lock ownership checks through `Client.IsFileLockedByCurrentCommitter`, and `tools.SetFileWriteFlag`.

Risks and edge cases: Permission changes ignore missing files but return other errors. Cached patterns require explicit refresh elsewhere after attribute changes. `fixFileWriteFlags` accepts `absPath` but enumerates from `workingDir`, so directory-scoped behavior depends on `git.NewLsFiles` semantics rather than `absPath` filtering.

Test signals: No direct tests in this subset. Behavior depends on broader locking checkout/attribute integration tests elsewhere.
