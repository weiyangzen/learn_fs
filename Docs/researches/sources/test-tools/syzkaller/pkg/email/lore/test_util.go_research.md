# sources/test-tools/syzkaller/pkg/email/lore/test_util.go

Purpose: `test_util.go` provides helpers for lore poller tests to create a local git-backed email archive.

Important APIs/types/functions: `TestLoreArchive` wraps `*vcs.TestRepo`. `NewTestLoreArchive` initializes a test repo and checks out `master`. `SaveMessage` saves using current time; `SaveMessageAt` writes raw message content to file `m`, stages it, and commits with a controlled commit date.

Control flow and state: each saved message overwrites `m` and creates a new commit, matching the archive reader convention in `ReadArchive`. Assertions ensure file writes succeed before committing.

Dependencies and integration: this file depends on `vcs.MakeTestRepo`, git commands through the test repo helper, `os.WriteFile`, and `filepath.Join`. It is test-only and supports `poller_test.go`.

Risks: helper correctness depends on the `vcs.TestRepo` implementation and local git availability in tests. It intentionally sets broad file permissions for the temporary file. There are no standalone tests, but it is exercised by poller tests.
