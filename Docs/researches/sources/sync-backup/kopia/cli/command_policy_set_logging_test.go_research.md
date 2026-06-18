<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_logging_test.go

Purpose: integration test for logging policy display, inheritance, overrides, inherit reset, and invalid numeric values.

Important APIs/types/functions: `TestSetLoggingPolicy`, `compressSpaces`, `testenv.NewCLITest`, `policy show`, and `policy set`.

Control flow: the test creates a repository, checks default global logging detail rows, checks inherited values for a temp directory, sets all six logging detail flags on the directory, verifies target-defined rows, resets one entry field to inherit, and asserts failures for negative, too-large, and nonnumeric inputs.

State/persistence behavior: mutates one local policy while observing effective inherited values from the global policy. Display assertions normalize repeated spaces to reduce formatting brittleness.

Dependencies/integration: spans `policy set`, `policy show`, policy inheritance, and display formatting. Risks/test signals: assertions depend on current default policy numeric detail levels and exact row labels.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging_test.go -->
