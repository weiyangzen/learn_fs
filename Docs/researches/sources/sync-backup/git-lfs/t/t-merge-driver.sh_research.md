# sources/sync-backup/git-lfs/t/t-merge-driver.sh

## Purpose

Tests `git lfs merge-driver` behavior for successful merges, explicit Git merge programs, custom merge programs, conflicts, and non-pointer inputs when LFS tracking is added after file history exists.

## Important APIs, control flow, and dependencies

Helper functions `setup_successful_repo`, `setup_custom_repo`, and `setup_conflicting_repo` create diverged branches with edited `a.dat`, optionally tracking LFS later. Tests configure `merge.lfs.driver` with `git lfs merge-driver --ancestor %O --current %A --other %B --marker-size %L --output %A` and optional `--program` commands, merge `other`, compare worktree content to expected merged/conflicted files, and assert pointer/local object results.

## State, dependencies, integration points, risks, and test signals

State includes branch histories, LFS-tracked pointer blobs, non-pointer historical blobs, merge output file, local LFS objects, and configured merge driver command. Integration points are Git merge driver placeholders, pointer smudge/clean for merge inputs, custom program substitution, conflict marker handling, and post-merge pointer storage. Risks include losing content when inputs are non-pointers, not propagating merge conflicts, quoting custom programs incorrectly, or writing wrong pointer OID. Signals are merge success/failure, `diff -u` against expected content, conflict-marker normalized diffs, and pointer/object assertions.
