# sources/sync-backup/syncthing/cmd/stdiscosrv/scripts/preinst

Purpose: Debian-style package pre-install script for the discovery server service account.

Important commands: `addgroup --system syncthing` and `adduser --system --home /var/lib/syncthing-discosrv --ingroup syncthing syncthing-discosrv`.

Control flow and state: the script creates the shared `syncthing` system group and a dedicated `syncthing-discosrv` system user with home/state directory `/var/lib/syncthing-discosrv`.

Dependencies/integration: supports the systemd unit's `User`, `Group`, and `WorkingDirectory` assumptions.

Risks and test signals: no shell strict mode is set, and behavior depends on platform-specific `addgroup`/`adduser` tools. It is packaging glue rather than Go runtime code; no tests are present.
