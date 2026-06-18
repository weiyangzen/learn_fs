# sources/user-network-fs/rclone/cmd/ncdu/ncdu_unsupported.go

Purpose: unsupported-platform stub for `ncdu` on Plan 9, js, and AIX builds.

Important behavior: package init is empty and no command is registered.

Control flow/state: no runtime behavior and no persistence. It prevents dependencies such as tcell/clipboard from being required where unsupported.

Dependencies/integration: build tags select this file instead of the real UI. Risks are command absence on those platforms needing clear documentation. Coverage is by build matrix.
