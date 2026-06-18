<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_delete_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_delete_cmd_test.py

Purpose: verifies `borg repo-delete` confirmation protection and final repository removal.

Important APIs: `cmd`, `create_regular_file`, `CancelledByUser`, `BORG_DELETE_I_KNOW_WHAT_I_AM_DOING`, and `RK_ENCRYPTION`.

Control flow: creates a repository and two archives, sets confirmation env var to `no` and expects cancellation, verifies the repository still exists, then sets the env var to `YES`, runs `repo-delete`, and asserts the repository path no longer exists.

State and persistence: deletion mutates/removes the repository directory; cancellation must not.

Dependencies/integration: depends on env-driven destructive operation confirmation and fork/non-fork error behavior. Risks include accidental deletion without confirmation or incomplete deletion. Test signals are expected exception/exit code and filesystem existence.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_delete_cmd_test.py -->
