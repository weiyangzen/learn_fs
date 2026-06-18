# sources/test-tools/syzkaller/pkg/vcs/vcs_test.go

## Purpose

This test file covers shared VCS helpers that are not specific to `gitRepo` internals.

## Important APIs, Types, And Functions

Tests include `TestPatch`, `TestPatchForbidden`, `TestCanonicalizeCommit`, `TestCheckRepoAddress`, `TestCheckBranch`, `TestCheckCommitHash`, `TestCommitLink`, `TestFileLink`, and `TestParseMaintainersLinux`. `testPredicate` is a table helper.

## Control Flow, State, Dependencies, And Integration

Patch tests use temp directories with and without initialized Git repos and verify content changes plus already-applied detection. Forbidden patch tests target `.git` and path traversal. Link tests verify output for GitHub, kernel.org, googlesource, fuchsia, cgit, git SSH, and unsupported URLs.

## Risks And Test Signals

The tests protect security-sensitive patch path handling and public dashboard link generation. They also fix the approximate validation contract for repository strings, branch names, and hashes. Maintainer parsing tests cover role-to-To/Cc behavior, especially LKML handling.
