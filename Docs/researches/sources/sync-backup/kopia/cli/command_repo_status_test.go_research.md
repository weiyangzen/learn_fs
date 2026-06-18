<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_status_test.go -->
# sources/sync-backup/kopia/cli/command_repo_status_test.go

Purpose: smoke test for repository status text and JSON output.

Important APIs/types/functions: `TestRepoStatusJSON`, `cli.RepositoryStatus`, `testenv.NewCLITest`, and `testutil.MustParseJSONLines`.

Control flow: the test creates a filesystem repository, runs `repo status` in text mode, then runs `repo status --json` and parses the output into `cli.RepositoryStatus`.

State/persistence behavior: creates and connects a repository, then reads connection/config metadata. No repository parameters are changed.

Dependencies/integration: covers repository create, status, JSON output, and config file handling. Risks/test signals: it validates JSON parseability but does not assert specific status fields, so it catches gross serialization failures rather than semantic regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_status_test.go -->
