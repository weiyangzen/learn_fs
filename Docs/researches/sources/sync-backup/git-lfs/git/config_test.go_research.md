<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config_test.go -->
# sources/sync-backup/git-lfs/git/config_test.go

## Research

This test file validates the read-only guard in `git.Configuration`. It creates `NewReadOnlyConfig`, attempts `SetLocal`, and expects `ErrReadOnly`.

The test is intentionally narrow and avoids invoking real Git. It protects the mutation guard used when code needs a config reader that cannot write. Gaps include all find/set/unset command construction, source loading, `.lfsconfig` fallbacks, file/worktree scopes, and version caching.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config_test.go -->
