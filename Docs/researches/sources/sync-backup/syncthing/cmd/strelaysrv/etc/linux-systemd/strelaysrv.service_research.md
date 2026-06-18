# sources/sync-backup/syncthing/cmd/strelaysrv/etc/linux-systemd/strelaysrv.service

Purpose: systemd unit for running the Syncthing relay server as a hardened service.

Important directives: `WorkingDirectory=/var/lib/syncthing-relaysrv`, `EnvironmentFile=/etc/default/syncthing-relaysrv`, `ExecStart=/usr/bin/strelaysrv -nat=${NAT} $RELAYSRV_OPTS`, `User=syncthing-relaysrv`, `Group=syncthing`, `ReadWritePaths=/var/lib/syncthing-relaysrv`, and alias `syncthing-relaysrv.service`.

Control flow: systemd starts the relay after network target and installs it under multi-user target.

State and persistence: relay keys and runtime files are expected under `/var/lib/syncthing-relaysrv`.

Dependencies/integration: matches the packaging preinstall script and `strelaysrv` flags, including NAT enablement via environment.

Risks and test signals: hardened sandboxing limits filesystem/device exposure. Startup depends on `/etc/default/syncthing-relaysrv` and writable state directory. No direct automated tests cover this unit.
