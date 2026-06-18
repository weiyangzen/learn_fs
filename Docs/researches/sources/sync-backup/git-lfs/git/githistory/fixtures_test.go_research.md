# sources/sync-backup/git-lfs/git/githistory/fixtures_test.go

Purpose: helper functions for githistory tests to copy fixture repositories, open object databases, and assert blob, commit, tree, and ref state.

Important APIs/types/functions: `DatabaseFromFixture`, `AssertBlobContents`, `AssertCommitParent`, `AssertCommitTree`, `AssertRef`, `HexDecode`, `copyToTmp`, `copyDir`, and `copyFile`.

Control flow: fixtures are recursively copied to a temp directory, opened with `gitobj.FromFilesystem`, and used by tests. Assertion helpers traverse trees path component by path component, decode SHAs, invoke `git rev-parse` for refs, and compare against expected bytes or contents.

State/persistence behavior: creates mutable temp copies under the OS temp directory and preserves file modes. No cleanup helper is present here; test temp artifacts are managed by OS/test lifecycle rather than `t.TempDir`.

Dependencies/integration: depends on `gitobj`, local `git`, `os/exec`, and `testify/assert`. It is central to `rewriter_test.go` and `ref_updater_test.go`.

Risks/test signals: recursive copy is simple and does not preserve symlink semantics specially. `AssertRef` depends on `db.Root()` and Git being able to run in that root. Helper failures call `t.Fatalf`, giving direct test failure signals.
