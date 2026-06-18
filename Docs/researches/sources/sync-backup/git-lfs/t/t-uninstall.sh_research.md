<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall.sh -->
# sources/sync-backup/git-lfs/t/t-uninstall.sh

Purpose: tests `git lfs uninstall` for global, local, skip-repo, hook-only, inaccessible local storage, and explicit `--file` scopes.

Important APIs/functions: uses `git lfs install`, `git lfs uninstall`, hook files, Git config list/get, permission manipulation, and scope flags such as `--local`, `--skip-repo`, and `--file`.

Control flow: outside-repo cases verify global cleanup and no access requirement for `.git/lfs`. Inside-repo cases check skip-repo behavior, default pre-push hook removal, non-LFS hook preservation, hook cleanup, local-only uninstall, conflicting scopes, and uninstalling from a specified config file.

State and persistence: mutates global fake HOME config, local `.git/config`, hook files, and custom config files.

Dependencies and integration points: integrates with installer/uninstaller config scope logic, hook template detection, permission handling, and Git config file writing.

Risks: uninstall must avoid deleting user hooks or wrong-scope filters while still removing LFS-managed entries cleanly.

Test signals: ten cases cover outside/inside repository behavior, inaccessible `.git/lfs`, skip-repo, pre-push and hook cleanup, local scope, conflicting scope, and explicit config file uninstall.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-uninstall.sh -->
