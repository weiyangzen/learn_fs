# sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/commit-msg

## Purpose

This Git commit-msg hook inserts a Gerrit `Change-Id` when missing and appends the author's `Signed-off-by` line when absent.

## Important APIs, Types, and Functions

Shell functions include `add_ChangeId`, `_gen_ChangeIdInput`, `_gen_ChangeId`, and `add_SignOffBy`. `CHANGE_ID_AFTER` controls footer insertion order. `MSG` is the commit message file path from Git.

## Control Flow

`add_ChangeId` strips comments/diffs/signoffs to determine whether there is a meaningful message, respects `gerrit.createChangeId=false`, skips if a Change-Id already exists, generates an ID from tree/parent/author/committer/message data, and uses AWK to insert it into the footer. `add_SignOffBy` derives the author identity and appends it if absent.

## State and Persistence Behavior

It mutates the commit message file in place. It does not change repository files directly.

## Dependencies and Integration Points

It depends on POSIX shell tools, `git`, `sed`, `awk`, and Gerrit review conventions. `install_git_hooks.sh` installs it into `.git/hooks/commit-msg`.

## Risks and Edge Cases

Footer parsing is complex and inherited from older Gerrit hook code. Automatically appending Signed-off-by may surprise contributors if signoff policy changes. It assumes the message file is writable and `git var` identity is configured.

## Test Signals

Hook tests should feed messages with no footer, existing Change-Id, Signed-off-by, issue footers, comment-only messages, and diff trailers, then verify final footer ordering.
