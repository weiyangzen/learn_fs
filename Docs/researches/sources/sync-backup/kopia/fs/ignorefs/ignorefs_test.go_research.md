## sources/sync-backup/kopia/fs/ignorefs/ignorefs_test.go

Purpose: table-driven behavioral tests for `ignorefs.New` over a mock filesystem.

Important APIs/types/functions: `setupFilesystem`, policy fixtures (`defaultPolicy`, `rootAndSrcPolicy`, `oneFileSystemPolicy`), `cases`, `TestIgnoreFS`, `walkTree`, `verifyDirectoryTree`, and `addAndSubtractFiles`.

Control flow, state, and persistence: each test builds an in-memory `mockfs.Directory`, optionally mutates it with ignore files, symlinks, and nested directories, wraps it with `ignorefs`, walks the resulting tree, and compares sorted paths against expected additions/removals. There is no persistence beyond the mock tree and policy fixtures.

Dependencies and integration points: exercises `ignorefs` through public `fs.Directory` traversal helpers and `snapshot/policy` trees. Uses mock devices to validate one-filesystem semantics.

Risks and test signals: provides strong coverage of wildcard matching, directory exclusion, inherited ignore files, nested policy overrides, negated patterns, symlinked dot-ignore files, max-file-size filtering, and device filtering. The test suite is especially useful as a compatibility signal with `.gitignore`-style behavior, including the known behavior that empty included directories may remain visible.
