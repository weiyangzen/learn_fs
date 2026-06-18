<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password_test.go -->
# sources/sync-backup/kopia/cli/command_repository_change_password_test.go

Purpose: format-specific integration test for repository password changes and old/new password behavior across clients.

Important APIs/types/functions: `TestRepositoryChangePassword`, `formatSpecificTestSuite`, `testenv.NewCLITest`, and `format.FormatVersion1`.

Control flow: the test creates two CLI environments/runners, creates a filesystem repository with format cache disabled, rejects change-password for format v1, otherwise connects a second client, changes the password from the first client, verifies the second client and new connections with the old password fail, then verifies a new connection succeeds with `KOPIA_PASSWORD=newPass`.

State/persistence behavior: changes the repository password and local password state for `env1`; `env2` uses stale credentials and fails after the format update.

Dependencies/integration: covers format manager password changes, connection cache behavior, environment-supplied password, and snapshot listing as an operational probe. Risks/test signals: relies on disabled format cache to make password change immediately visible.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_change_password_test.go -->
