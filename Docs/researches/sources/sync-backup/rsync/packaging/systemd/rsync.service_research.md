
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.service -->
# Research: sources/sync-backup/rsync/packaging/systemd/rsync.service

## Purpose
`packaging/systemd/rsync.service` defines a standalone systemd service for running rsync daemon mode as a long-running process.

## Important APIs, Types, and Functions
The unit has `[Unit]`, `[Service]`, and `[Install]` sections. Key directives are `ConditionPathExists=/etc/rsyncd.conf`, `After=network.target`, `Documentation=man:rsync(1) man:rsyncd.conf(5)`, `ExecStart=/usr/bin/rsync --daemon --no-detach`, `Restart=on-failure`, `ProtectSystem=full`, `PrivateDevices=on`, and `NoNewPrivileges=on`.

## Control Flow
systemd starts this service only when `/etc/rsyncd.conf` exists. The rsync process remains in the foreground due to `--no-detach`; systemd restarts it after failures with a one-second delay. The install target is `multi-user.target`.

## State and Persistence
The unit itself does not store state. Runtime state belongs to systemd and the rsync daemon. It hardens filesystem/device access by making major system paths read-only and hiding devices.

## Dependencies and Integration Points
It integrates with Linux systemd packaging and `/etc/rsyncd.conf`. It conflicts operationally with the socket-activation unit because the socket unit declares a conflict with this service.

## Risks
`ProtectSystem=full` and `PrivateDevices=on` are secure defaults but can break modules that need writes under protected paths or device access; admins must override via drop-ins. The hard-coded `/usr/bin/rsync` path must match package layout. `After=network.target` does not guarantee fully configured network in all environments.

## Test Signals
Package tests should run `systemd-analyze verify`, start the service with a minimal `/etc/rsyncd.conf`, verify foreground daemon behavior, restart-on-failure, and check hardening compatibility for expected module paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.service -->
