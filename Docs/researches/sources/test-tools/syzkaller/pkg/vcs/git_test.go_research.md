# sources/test-tools/syzkaller/pkg/vcs/git_test.go

## Purpose

`git_test.go` provides broad unit/integration coverage for Git metadata parsing, release tag sorting, lookup helpers, diff parsing, object reads, merge-base handling, custom refs, tag fetches, and base-commit inference.

## Important APIs, Types, And Functions

Tests include `TestGitParseCommit`, `TestGitParseReleaseTags`, `TestGetCommitsByTitles`, `TestContains`, `TestLatestCommits`, `TestObject`, `TestMergeBase`, `TestGitCustomRefs`, `TestGitRemoteTags`, `TestGitFetchShortHash`, `TestParseGitDiff`, `TestGitFileHashes`, `TestBaseForDiff`, and `TestBaseForDiffMerge`.

## Control Flow, State, Dependencies, And Integration

The file uses real temp Git repositories through `MakeTestRepo`. It creates branches, tags, custom refs, empty commits, content commits, diffs, merge commits, and conflict resolutions. Assertions verify both metadata values and repository graph behavior.

## Risks And Test Signals

The tests cover many operational edge cases: backported title canonicalization via lookup, short commit fetches, custom refs, tag reachability, newly created files in diffs, unknown blob hashes, repeated file modifications, and merge-derived bases. They depend on Git output formats and wall-clock seconds for one sort test.
