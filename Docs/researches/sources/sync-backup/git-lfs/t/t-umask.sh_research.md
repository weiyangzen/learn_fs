<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-umask.sh -->
# sources/sync-backup/git-lfs/t/t-umask.sh

Purpose: verifies Git LFS-created files and directories honor process `umask` and Git `core.sharedRepository`.

Important APIs/functions: defines `clean_setup`, `perms_for`, and `assert_dir_perms`; uses `umask`, `git config core.sharedRepository`, LFS tracking/commit, and filesystem mode inspection.

Control flow: creates clean repos under different `umask` and shared-repository settings, runs LFS operations that create object files/directories, and checks resulting modes.

State and persistence: writes LFS object storage directories/files and Git config; relies on POSIX permissions.

Dependencies and integration points: integrates with LFS file creation helpers, repository permission fetcher, Git shared repository config, and OS mode behavior.

Risks: incorrect permissions can expose private media, prevent collaborators from reading shared repos, or break object creation under restrictive umasks.

Test signals: four cases cover umask for files and directories plus sharedRepository for files and directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-umask.sh -->
