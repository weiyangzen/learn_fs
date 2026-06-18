# sources/sync-backup/git-lfs/t/t-install-worktree.sh

## Purpose

Tests `git lfs install --worktree` on Git versions with worktree config support. It verifies outside-repo failure, single and multiple worktree config scopes, refusal without `extensions.worktreeConfig`, and conflicts with other install scopes.

## Important APIs, control flow, and dependencies

The script requires Git 2.20+, creates repos and linked worktrees, mutates global/local filter values, enables `core.repositoryformatversion=1` and `extensions.worktreeConfig=true`, runs `git lfs install --worktree`, and compares `git config`, `--local`, `--worktree`, and `--global` values. It also runs conflicting option combinations with `--local`, `--system`, and `--file`.

## State, dependencies, integration points, risks, and test signals

State includes global config, local repo config, worktree-specific config, linked worktree metadata, and command output files. Integration points are Git worktree config extension, filter installation scope selection, repository discovery, and option validation. Risks include overwriting global/local config, allowing worktree config without the extension, or accepting multiple scopes. Signals are exact filter value comparisons, nonzero outside-repo/error cases, and exact conflict error text.
