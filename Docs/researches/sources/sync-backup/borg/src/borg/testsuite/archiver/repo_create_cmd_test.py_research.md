<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_create_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_create_cmd_test.py

Purpose: tests repository creation failure paths and keyfile overwrite protection.

Important APIs: `cmd`, `FlexiKey.create`, `patch`, `CancelledByUser`, `Error`, `RK_ENCRYPTION`, `KF_ENCRYPTION`, `KF_LOCATION`, and `BORG_KEY_FILE`.

Control flow: `test_repo_create_interrupt` patches key creation to raise `EOFError`, expects cancellation/exit code, and asserts no repository path remains. `test_repo_create_requires_encryption_option` verifies missing encryption fails. `test_repo_create_refuse_to_overwrite_keyfile` creates one keyfile through `BORG_KEY_FILE`, then attempts a second repo-create pointing to the same file and verifies it fails without modifying file contents.

State and persistence: repository directory creation is rolled back on interrupted setup; explicit keyfile content must remain unchanged.

Dependencies/integration: depends on non-binary patchability, key creation, environment variables, fork/non-fork error behavior, and keyfile storage. Risks include partial repository creation, unsafe key overwrite, and divergent binary exit handling. Test signals are existence checks, exit codes/exceptions, and before/after keyfile content equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_create_cmd_test.py -->
