<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_splitter_test.go

Purpose: integration test for splitter policy default display, local override, inherit reset, and invalid algorithm rejection.

Important APIs/types/functions: `TestSetSplitterPolicy`, `testenv.NewCLITest`, `policy show`, `policy set`, and `compressSpaces`.

Control flow: the test creates a repository, verifies the global repository-default splitter row, verifies local inherited display for a temp directory, sets `FIXED-4M`, verifies it is target-defined, resets with `inherit`, and expects failure for a nonexistent splitter.

State/persistence behavior: creates and clears a local splitter override while preserving global default behavior.

Dependencies/integration: spans CLI enum validation, policy persistence, inheritance, and display formatting. Risks/test signals: test assumes `FIXED-4M` is present in the supported splitter registry.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_splitter_test.go -->
