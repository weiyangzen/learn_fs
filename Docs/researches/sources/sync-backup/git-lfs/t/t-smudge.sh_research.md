<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-smudge.sh -->
# sources/sync-backup/git-lfs/t/t-smudge.sh

Purpose: validates the `git lfs smudge` filter and checkout-time download behavior, including temp-file writes, invalid pointers, pointer extensions, include/exclude filters, skip modes, failure tolerance, and non-origin remotes.

Important APIs/functions: uses `setup_remote_repo_with_file`, `clone_repo`, `git lfs smudge`, `git lfs pull`, `git lfs install`, `GIT_LFS_SKIP_SMUDGE`, include/exclude config, pointer helpers, and local/server object assertions.

Control flow: early cases smudge valid pointers and temp-file paths, reject malformed pointer input, and process extension-bearing pointers. Include/exclude tests configure path filters and verify selected files download or stay as pointers. Skip tests exercise env/config-driven smudge bypass. Clone and failure cases check checkout behavior when downloads are filtered or unavailable. The non-origin case verifies endpoint resolution outside the default remote.

State and persistence: mutates local LFS media, `.git/config`, working tree files, env vars, and remote LFS object availability. Some tests deliberately delete local objects or server objects.

Dependencies and integration points: exercises clean/smudge filters, pointer parser, extension framework, checkout filter process, transfer queue, include/exclude path matching, and remote endpoint resolution.

Risks: smudge failures directly affect checkout correctness. Include/exclude and skip behavior can leave pointers where contents are expected, while extension or temp-file mistakes can corrupt working-tree output.

Test signals: nine integration blocks cover normal smudge, temp file handling, invalid pointers, extensions, include/exclude, skip, clone filters, skipped download failures, and non-origin remotes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-smudge.sh -->
