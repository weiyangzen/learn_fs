# sources/sync-backup/restic/cmd/restic/cmd_key.go

Purpose: registers the parent `restic key` command and its key-management subcommands.

Important APIs/types/functions: `newKeyCommand` creates a cobra command with subcommands from `newKeyListCommand`, `newKeyAddCommand`, `newKeyRemoveCommand`, and `newKeyPasswdCommand`.

Control flow and state: the parent command does not itself open repositories or mutate state; all behavior is delegated to subcommands.

Dependencies and integration points: integrates with command grouping and cobra's command hierarchy. The child commands share repository key operations from `internal/repository`.

Risks: missing child registration would silently remove key functionality from the CLI. Parent has no `RunE`, so invoking `restic key` depends on cobra help/default behavior.

Test signals: key integration tests exercise child commands and flags tests parse root command children.
