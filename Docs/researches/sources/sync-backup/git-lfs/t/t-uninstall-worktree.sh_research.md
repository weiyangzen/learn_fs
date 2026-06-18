<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree.sh -->
# sources/sync-backup/git-lfs/t/t-uninstall-worktree.sh

Purpose: validates `git lfs uninstall --worktree` across outside-repo, single worktree, multiple worktrees, missing extension, and conflicting-scope scenarios.

Important APIs/functions: uses `git worktree`, `git lfs install --worktree`, `git lfs uninstall --worktree`, Git config inspection, and hook/filter assertions.

Control flow: cases assert outside-repo errors, then install/uninstall worktree-scoped filters in one worktree and multiple linked worktrees, checking that only worktree-local config is removed. It also verifies behavior without `extensions.worktreeConfig` and with incompatible flags.

State and persistence: writes per-worktree config, common repo config, hooks, and linked worktree metadata.

Dependencies and integration points: integrates with Git worktree config files, LFS filter config, hook management, and scope validation.

Risks: scope bugs can remove filters for all worktrees, fail to clean a worktree, or conflict with local/global/system uninstall flags.

Test signals: five cases cover outside repo, single worktree, multiple worktrees, missing extension, and conflicting scope.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall-worktree.sh -->
