<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs_test.go -->
# sources/sync-backup/git-lfs/fs/fs_test.go

## Research

This test file covers two `fs.go` behaviors. The decode tests verify that non-octal paths remain unchanged and octal byte escapes are converted back into bytes/characters, including multiple escapes. `TestRepositoryPermissions` verifies executable permissions are derived from stored non-executable repository permissions.

Tests are pure except for mode constants. They protect Windows/Git quoted path decoding used when Git escapes non-ASCII filenames. Gaps include object path creation, empty object handling, alternate reference resolution, cleanup pruning, common-dir redirects, callback error propagation, and repository permission interactions with real directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs_test.go -->
