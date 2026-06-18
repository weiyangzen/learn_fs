# sources/sync-backup/restic/cmd/restic/cmd_repair.go

Purpose: registers the parent `restic repair` command and its repair subcommands.

Important APIs/types/functions: `newRepairCommand` registers `repair index`, `repair packs`, and `repair snapshots`.

Control flow and state: parent command only defines help text and command grouping; all repository mutation occurs in child subcommands.

Dependencies and integration points: integrates repair functionality into the cobra command tree.

Risks: missing subcommand registration removes repair tools. The parent has no run behavior.

Test signals: repair subcommand integration tests cover child behavior; flags tests parse command tree help.
