
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync@.service -->
# Research: sources/sync-backup/rsync/packaging/systemd/rsync@.service

## Purpose
`packaging/systemd/rsync@.service` is the per-connection systemd template used by `rsync.socket` for socket-activated rsync daemon sessions.

## Important APIs, Types, and Functions
Key directives are `ExecStart=-/usr/bin/rsync --daemon`, `StandardInput=socket`, `StandardOutput=inherit`, `StandardError=journal`, `ProtectSystem=full`, `PrivateDevices=on`, and `NoNewPrivileges=on`.

## Control Flow
For each accepted socket connection, systemd starts an instance of this template and attaches the socket to stdin. The leading `-` in `ExecStart` tells systemd to treat non-zero rsync exits as non-fatal for unit failure accounting.

## State and Persistence
No persistent state is written by the unit. Each service instance is transient per connection, with logs going to journald and output inherited as configured.

## Dependencies and Integration Points
It pairs with `rsync.socket` and runs `/usr/bin/rsync --daemon` in socket mode. It shares hardening assumptions with the standalone service.

## Risks
The template lacks `ConditionPathExists=/etc/rsyncd.conf`, so behavior without a config depends on rsync defaults/errors. The `-` prefix can hide failure status from systemd-level monitoring. Hardening may block unusual daemon modules without drop-in overrides.

## Test Signals
Verify socket activation with `systemd-analyze verify`, a real TCP connection, journald logging, expected exit status treatment, and module access under the hardening directives.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync@.service -->
