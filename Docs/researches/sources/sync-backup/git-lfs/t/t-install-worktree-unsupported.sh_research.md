# sources/sync-backup/git-lfs/t/t-install-worktree-unsupported.sh

## Purpose

Version-gated test for Git versions without worktree-specific config support. It verifies `git lfs install --worktree` fails with an error instead of silently writing an unsupported scope.

## Important APIs, control flow, and dependencies

The script uses `ensure_git_version_isnt $VERSION_HIGHER "2.20.0"`, initializes a repo, runs `git lfs install --worktree`, captures stderr, and asserts nonzero status plus error text containing `--worktree`.

## State, dependencies, integration points, risks, and test signals

State is only repository config and command output. Integration points are Git version detection and `git config --worktree` availability. Risks include silently writing local/global config or reporting success on unsupported Git. Signals are nonzero exit status and greps for `error` and `--worktree`.
