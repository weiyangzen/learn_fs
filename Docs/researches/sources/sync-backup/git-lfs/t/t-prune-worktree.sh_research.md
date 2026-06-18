# sources/sync-backup/git-lfs/t/t-prune-worktree.sh

Purpose: verifies `git lfs prune` retains LFS objects referenced by linked worktrees and by staged files in those worktrees, including when the primary repository is bare.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `lfstest-testutils addcommits`, `calc_oid`, `git config lfs.fetchrecent*`, `lfs.fetchexclude`, `git worktree add/remove/prune`, `git add`, and `git lfs prune --dry-run`.

Control flow: the main test creates branches with included and excluded `.dat` objects, configures recent-object pruning to be aggressive, and first records the prune count before adding worktrees. It then adds worktrees for two branches, stages new LFS files inside them, and expects retention counts to increase. Removing a worktree and pruning Git worktree metadata should progressively reduce retained counts. The bare-main test converts the main clone to a bare repository, uses one linked worktree, stages a file, and expects all objects to be retained.

State/persistence behavior: relevant state spans shared LFS object storage, main repo refs, linked worktree HEAD/index files, Git worktree metadata, and fetch-exclude configuration. Dry-run logs are used to assert object accounting without deleting files.

Dependencies/integration points: integrates Git worktree metadata discovery, LFS prune reachability scanning, staged pointer parsing, fetch include/exclude rules, and bare repository layout.

Risks/test signals: regressions can delete objects needed by other worktrees or fail to release objects after worktree metadata is removed. Count-based assertions are sensitive to fixture changes but give clear retention signals.
