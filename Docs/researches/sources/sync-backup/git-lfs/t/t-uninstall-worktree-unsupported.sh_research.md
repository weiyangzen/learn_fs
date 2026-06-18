<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree-unsupported.sh -->
# sources/sync-backup/git-lfs/t/t-uninstall-worktree-unsupported.sh

Purpose: checks `git lfs uninstall --worktree` failure behavior when Git does not support or enable the required worktree config extension.

Important APIs/functions: uses `git init`, `git lfs install/uninstall --worktree`, and direct config extension checks.

Control flow: initializes a repo with unsupported worktree configuration state, invokes uninstall with worktree scope, and expects a clear failure.

State and persistence: mutates repository config but should not leave partial filter/hook removal after unsupported operation failure.

Dependencies and integration points: integrates with Git worktree config extension detection and LFS install/uninstall scope handling.

Risks: unsupported worktree operations could delete local/global config unexpectedly or leave filters half-installed.

Test signals: one unsupported-extension failure case.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree-unsupported.sh -->
