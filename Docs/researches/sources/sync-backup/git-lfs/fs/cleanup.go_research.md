<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/cleanup.go -->
# sources/sync-backup/git-lfs/fs/cleanup.go

## Research

`cleanup.go` prunes stale temporary LFS files. `Filesystem.cleanupTmp` resolves the temp directory, ignores missing directories, walks it with `tools.FastWalkDir`, tracks traversed directory metadata, removes temp files whose prefix is a 64-character OID when the final object already exists, and removes files older than one hour while sparing young subdirectories.

Persistent effects are deletions under `.git/lfs/tmp`. State is walk-local plus the filesystem’s path helpers. Integration is `Filesystem.Cleanup` and `Configuration.Cleanup`, also called from process shutdown. Risks include concurrent transfers using temp files, reliance on directory mtime to protect hard-linked active files, walk error handling through a shared variable, OID prefix heuristic, and `os.RemoveAll` errors ignored. There is no direct test in this subset; integration should verify active downloads are not pruned and old complete temp files are removed.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/cleanup.go -->
