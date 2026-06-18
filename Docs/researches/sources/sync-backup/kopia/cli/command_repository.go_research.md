<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository.go -->
# sources/sync-backup/kopia/cli/command_repository.go

Purpose: top-level repository command registrar for `kopia repository` and alias `repo`.

Important APIs/types/functions: `commandRepository`, `setup`, and subcommand fields for connect, create, disconnect, repair, set-client, set-parameters, status, sync-to, throttle, change-password, validate-provider, and upgrade.

Control flow: setup creates the parent command and delegates setup to each subcommand in a fixed order. There is no run method or state mutation in this file.

State/persistence behavior: none directly; it wires command handlers that manage repository config files, format blobs, storage, and runtime state elsewhere.

Dependencies/integration: central integration point for advanced app services and kingpin command tree construction. Risks/test signals: missing a subcommand registration here makes otherwise implemented functionality unreachable from CLI.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository.go -->
