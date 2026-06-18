
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.socket -->
# Research: sources/sync-backup/rsync/packaging/systemd/rsync.socket

## Purpose
`packaging/systemd/rsync.socket` defines systemd socket activation for rsync daemon connections on TCP port 873.

## Important APIs, Types, and Functions
The unit uses `[Socket]` directives `ListenStream=873` and `Accept=true`. The `[Unit]` section declares `Conflicts=rsync.service`, and `[Install]` uses `WantedBy=sockets.target`.

## Control Flow
When enabled, systemd listens on port 873. With `Accept=true`, each accepted connection starts an instance of the matching template service, `rsync@.service`, with the accepted socket passed as standard input.

## State and Persistence
The unit persists only as systemd configuration. Runtime listener state is owned by systemd.

## Dependencies and Integration Points
It integrates with `rsync@.service` by systemd naming convention and conflicts with the standalone `rsync.service` to prevent two listeners on the same port.

## Risks
Port 873 requires appropriate privileges/capabilities. `Accept=true` creates one service instance per connection, so resource limits and daemon config should be reviewed for high-connection environments. Socket activation bypasses the standalone service's `ConditionPathExists` check unless the template has equivalent validation.

## Test Signals
Run `systemd-analyze verify` on the socket and template together, enable/start the socket, connect to port 873, and verify an `rsync@...service` instance is spawned and exits correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/packaging/systemd/rsync.socket -->
