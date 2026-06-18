# sources/sync-backup/restic/cmd/restic/cmd_mount_disabled.go

Purpose: build-tag fallback for platforms without mount support.

Important APIs/types/functions: `registerMountCommand` is a no-op under `!darwin && !freebsd && !linux`.

Control flow and state: no command is added, no repository is opened, and no state changes occur.

Dependencies and integration points: shares the same symbol as `cmd_mount.go` so root command registration can call `registerMountCommand` unconditionally across builds.

Risks: platform build tags must remain complementary with the enabled file. Unsupported platforms silently omit the command.

Test signals: no direct tests here; successful cross-platform builds and flags tests exercise command tree consistency.
