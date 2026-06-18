<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-worktree.sh -->
# sources/sync-backup/git-lfs/t/t-worktree.sh

Purpose: verifies Git LFS behavior in Git linked worktrees, including object storage and hooks.

Important APIs/functions: uses `git worktree add`, `git lfs track`, commits, checkout/filter behavior, and `assert_hooks`.

Control flow: creates a primary repo and linked worktree, performs LFS operations in the worktree, and checks content/object behavior. A second test validates hook installation/availability for worktrees.

State and persistence: uses common Git dir plus per-worktree working trees/config, LFS media directories, and hook files.

Dependencies and integration points: integrates with Git worktree discovery, local media path resolution, filter execution, and hook installation.

Risks: worktree-specific gitdir indirection can misplace objects or hooks, especially with common-dir/shared config.

Test signals: two cases cover normal worktree LFS use and worktree hooks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-worktree.sh -->
