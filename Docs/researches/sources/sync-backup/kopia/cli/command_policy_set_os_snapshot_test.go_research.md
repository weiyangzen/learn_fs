<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_os_snapshot_test.go

Purpose: integration test for Volume Shadow Copy policy defaults, global overrides, inherited display, and local override.

Important APIs/types/functions: `TestSetOSSnapshotPolicy`, `testenv.NewCLITest`, `policy show`, `policy set`, and shared `compressSpaces`.

Control flow: the test creates a repository, verifies the global default `never`, sets global mode to `when-available`, verifies a temp directory inherits it, changes global mode to `always`, verifies inherited update, then sets local mode to `never` and checks it is target-defined.

State/persistence behavior: mutates global and local policy definitions and validates effective inherited policy output.

Dependencies/integration: covers setter, policy inheritance, and show formatting. Risks/test signals: it does not exercise platform-specific VSS execution; it only validates policy storage and display.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot_test.go -->
