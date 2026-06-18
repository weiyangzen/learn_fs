# sources/sync-backup/git-lfs/t/t-commit-delete-push.sh

## Purpose
Tests that `git lfs push` includes LFS objects reachable from history even if their files are later deleted before the push. This prevents lost objects for historical commits.

## Important APIs, Functions, and Control Flow
The test commits `deleted.dat`, checks dry-run output and pointer metadata, commits `added.dat`, checks dry-run includes both objects, removes `deleted.dat`, commits the deletion, checks dry-run again, then performs a real push and verifies both server objects exist.

## State, Persistence, and Dependencies
State includes a three-commit history, dry-run logs, server object store, and local pointers. Dependencies include `calc_oid`, `assert_pointer`, `assert_server_object`, and exact dry-run output.

## Integration Points, Risks, and Test Signals
Integration is with LFS object graph traversal for push. Signals are dry-run `push <oid> => <path>` lines, upload progress for two files, and server object assertions. Risks are exact output matching and reliance on historical path names after deletion.
