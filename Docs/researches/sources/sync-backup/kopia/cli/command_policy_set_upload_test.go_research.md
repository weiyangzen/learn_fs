<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_upload_test.go

Purpose: integration test for upload policy default display, inherited display, global overrides, and reset to default.

Important APIs/types/functions: `TestSetUploadPolicy`, `testenv.NewCLITest`, `policy show`, `policy set`, and `compressSpaces`.

Control flow: the test creates a repository, checks global upload defaults, checks inherited values on a temp directory, sets global max parallel snapshots, max file reads, and parallel threshold, verifies inherited display reflects the global changes, then resets all three with `default`.

State/persistence behavior: mutates only global upload policy and observes inherited effective policy for a local source.

Dependencies/integration: covers setter conversion from MiB to bytes and display via `units.BytesString`. Risks/test signals: display strings like `2.1 GB` and `4.3 GB` depend on unit formatting conventions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_upload_test.go -->
