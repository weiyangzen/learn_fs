<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-status.sh -->
# sources/sync-backup/git-lfs/t/t-status.sh

Purpose: validates `git lfs status` human, porcelain, and JSON output across clean, dirty, staged, partially staged, missing, unpushed, bare/no-worktree, deleted, file-directory conflict, and permission-change scenarios.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `git lfs status`, `git status`, pointer/object helpers, `git update-index`, and direct working-tree mutations.

Control flow: the suite builds repositories with LFS-tracked files and compares status output after edits, staging, partial staging, conversions between Git and LFS content, missing local objects, unpushed objects, deleted files, and permission mode changes. Output modes are validated separately for normal, porcelain, and JSON.

State and persistence: mutates index, working tree, local LFS media, commits, remotes, and file permissions. Some cases run in subdirectories or repositories without a checkout.

Dependencies and integration points: integrates with Git index diffing, pointer detection, local media lookup, transfer state, JSON formatting, path relativization, and permission mode logic.

Risks: status output is user-facing and script-facing. Regressions can misclassify staged/unstaged LFS transitions, hide missing media, produce invalid JSON, or report wrong paths from subdirectories.

Test signals: seventeen cases cover output formats, subdirectory and outside-repo behavior, initial commit state, duplicate contents, partial staging, LFS/Git conversions, missing/unpushed objects, bare/no-worktree, deletion, file-to-dir, and permission changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-status.sh -->
