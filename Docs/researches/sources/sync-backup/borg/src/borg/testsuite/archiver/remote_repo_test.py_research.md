<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/remote_repo_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/remote_repo_test.py

Purpose: smoke/integration tests for non-local repository backends: rclone, REST, SFTP, and S3.

Important APIs: `have_rclone`, `cmd`, `create_regular_file`, `assert_dirs_equal`, `changedir`, backend URLs from `BORG_TEST_*_REPO`, and optional `BORG_REMOTE_PATH`.

Control flow: each backend test creates files, points `archiver.repository_location` at the backend URL, runs `repo-create`, `create`, `repo-list`, `list`, `extract`, `delete`, and `repo-delete`. The rclone test validates installed rclone version using `rclone rc --loopback core/version`; REST sets `BORG_REMOTE_PATH` to the local borg executable when needed.

State and persistence: creates actual remote/backend repositories and removes archives/repositories at the end. Extraction writes to the local output path for content comparison.

Dependencies/integration: depends on external services or env vars, rclone version, remote transport implementations, and repository cleanup. Risks are environmental flakiness, partial cleanup after failures, and backend-specific metadata differences hidden by ignored flags/xattrs. Test signals are archive names in listings, file paths in archive lists, directory equality, and successful delete/repo-delete.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/remote_repo_test.py -->
