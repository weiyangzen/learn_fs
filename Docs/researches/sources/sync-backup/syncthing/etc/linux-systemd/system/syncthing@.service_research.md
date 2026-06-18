# sources/sync-backup/syncthing/etc/linux-systemd/system/syncthing@.service

## Purpose
This system-level systemd template runs Syncthing as a named user instance (`syncthing@<user>.service`). It includes extensive default hardening intended to reduce damage if the Syncthing process is compromised while still allowing normal file synchronization with user-specific permissions.

## Important APIs, Types, And Functions
The unit has `[Unit]`, `[Service]`, and `[Install]` sections. Core service settings include `User=%i`, log-format environment variables for syslog-friendly output, `ExecStart=/usr/bin/syncthing serve --no-browser --no-restart`, `Restart=on-failure`, `SuccessExitStatus=3 4`, and `RestartForceExitStatus=3 4`. Hardening directives include `ProtectSystem=full`, multiple `ProtectKernel*` options, `NoNewPrivileges=true`, `RestrictSUIDSGID=true`, `MemoryDenyWriteExecute=true`, `RestrictNamespaces=true`, `RestrictAddressFamilies=AF_INET AF_INET6 AF_NETLINK AF_UNIX`, capability bounding, `PrivateTmp=disconnected`, `PrivateDevices=true`, `PrivatePIDs=true`, `ProtectProc=invisible`, `ProcSubset=pid`, `SystemCallFilter=@system-service`, `SystemCallErrorNumber=EPERM`, `UMask=7027`, and `InaccessiblePaths=-/nonexistent`.

## Control Flow
Systemd starts the unit after `network.target`, as the instance user named by `%i`. Syncthing is run in foreground `serve` mode with browser opening and internal restart disabled, leaving restart supervision to systemd. Exit statuses 3 and 4 are treated as successful and also force restart, matching Syncthing's special restart/upgrade exit semantics. On failure, systemd restarts after one second, bounded by `StartLimitIntervalSec=60` and `StartLimitBurst=4`.

## State And Persistence Behavior
Syncthing state is stored in the target user's normal home/config locations unless overridden by drop-ins or environment. The unit itself does not define `StateDirectory`; it relies on user ownership and normal filesystem access. Hardening makes `/usr`, `/boot`, `/efi`, and `/etc` read-only and hides or restricts many kernel/system interfaces. The unit's `UMask=7027` restricts world-readable creation by default while still allowing Syncthing to explicitly chmod synchronized files.

## Dependencies And Integration Points
This is a packaging/deployment integration point for systemd systems. It integrates with journald through Syncthing log-format environment variables, systemd restart semantics, systemd sandboxing features, and optional drop-in overrides for ownership synchronization or custom shared paths. Comments point users to `systemd-analyze security` and drop-in locations.

## Risks And Edge Cases
The hardening is intentionally best-effort and may be ignored by old systemd/kernel combinations. Some options can break advanced features: `MemoryDenyWriteExecute` can affect external tools if executed in-process context, `NoExecPaths` examples are commented because external file versioning may need arbitrary binaries, and capability settings require careful drop-ins for `syncOwnership`. `ProtectSystem=full` is safe for many cases, but stricter optional settings require explicit `ReadWritePaths`. `RestrictAddressFamilies` must continue allowing the address families Syncthing needs, including AF_NETLINK for interface discovery.

## Test Signals
Operational tests should run `systemctl start syncthing@USER.service`, inspect `journalctl --unit`, confirm restarts on Syncthing restart/upgrade exit codes, and run `systemd-analyze security`. Feature tests should cover normal syncing, discovery, QUIC/TCP connectivity, optional ownership sync when configured, and external versioning if users enable extra hardening.
