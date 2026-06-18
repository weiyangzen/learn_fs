# File Research: sources/virtualization/open-iscsi/usr/iscsid.h

## Purpose
`iscsid.h` exposes daemon-wide globals shared by `iscsid.c` and supporting modules.

## Exports
It declares the global IPC implementation pointer `ipc`, defines `struct iscsi_daemon_config` with config file, PID file, initiator name, initiator alias, and safe logout flag, and declares global `dconfig`.

## Integration Notes
The header is included by logging and daemon-adjacent modules that need access to daemon configuration or the selected kernel IPC backend.
