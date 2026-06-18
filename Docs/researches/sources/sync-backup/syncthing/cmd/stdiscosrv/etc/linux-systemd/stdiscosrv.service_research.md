# sources/sync-backup/syncthing/cmd/stdiscosrv/etc/linux-systemd/stdiscosrv.service

Purpose: systemd unit for running the Syncthing discovery server as a hardened service.

Important directives: `WorkingDirectory=/var/lib/syncthing-discosrv`, `EnvironmentFile=/etc/default/syncthing-discosrv`, `ExecStart=/usr/bin/stdiscosrv $DISCOSRV_OPTS`, `User=syncthing-discosrv`, `Group=syncthing`, `ReadWritePaths=/var/lib/syncthing-discosrv`, and install alias `syncthing-discosrv.service`.

Control flow: systemd starts after `network.target` and launches the binary with options supplied by the environment file. The service participates in `multi-user.target`.

State and persistence: runtime data and database writes are confined to `/var/lib/syncthing-discosrv`; config is injected through `/etc/default/syncthing-discosrv`.

Dependencies/integration: integrates Linux packaging with the `stdiscosrv` binary and `scripts/preinst` user/group provisioning.

Risks and test signals: `ProtectSystem=strict`, `NoNewPrivileges`, private temp/devices, home protection, native syscall architecture, and W^X hardening reduce service attack surface. Operational risk is that missing environment file or incorrect writable path prevents startup. No automated tests target this unit file.
