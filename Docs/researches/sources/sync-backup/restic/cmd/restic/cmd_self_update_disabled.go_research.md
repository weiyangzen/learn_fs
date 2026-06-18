# sources/sync-backup/restic/cmd/restic/cmd_self_update_disabled.go

Purpose: build-tag fallback when `selfupdate` is not enabled.

Important APIs/types/functions: no-op `registerSelfUpdateCommand`.

Control flow and state: no command is registered; no filesystem, network, or repository state is touched.

Dependencies and integration points: provides the same symbol as the enabled self-update file so root command setup can be build-tag agnostic.

Risks: build tags must remain mutually exclusive and exhaustive. Users of builds without `selfupdate` will not see the command.

Test signals: command tree construction and cross-build compilation are the main validation signals.
