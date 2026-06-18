# sources/sync-backup/syncthing/cmd/strelaysrv/scripts/preinst

Purpose: package pre-install script for relay server service identity.

Important commands: creates the shared system group `syncthing` and system user `syncthing-relaysrv` with home `/var/lib/syncthing-relaysrv`.

Control flow and state: runs before package install to ensure the systemd unit's user/group and working directory ownership assumptions can be satisfied.

Dependencies/integration: supports `strelaysrv.service`.

Risks and test signals: no strict shell options and platform-specific account tools. No tests.
