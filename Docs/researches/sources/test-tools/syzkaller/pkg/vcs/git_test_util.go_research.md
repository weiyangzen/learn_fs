# sources/test-tools/syzkaller/pkg/vcs/git_test_util.go

## Purpose

`git_test_util.go` provides helpers for constructing and manipulating temporary Git repositories in VCS tests.

## Important APIs, Types, And Functions

`TestRepo` stores test state, directory, commit map, and backing `gitRepo`. `Git` runs Git commands. `MakeTestRepo` initializes a repo, configures user identity and disables auto maintenance. `CommitFileChange`, `CommitChange`, `CommitChangeAt`, `CommitChangeset`, `SetTag`, `SupportsBisection`, and `CreateTestRepo` build reusable histories. `FileContent.Apply` writes and stages files.

## Control Flow, State, Dependencies, And Integration

Helpers mutate real temp directories and use `filterEnv` to avoid caller Git environment leakage. `MakeTestRepo` uses `OptPrecious` and `OptDontSandbox` for local test control. The `Commits` map records expected branch/change commits for assertions.

## Risks And Test Signals

These helpers centralize assumptions about Git availability, default branch handling, author identity, and repository maintenance behavior. `FileContent.Apply` writes files directly and assumes parent directories exist. Failures here affect many VCS tests.
