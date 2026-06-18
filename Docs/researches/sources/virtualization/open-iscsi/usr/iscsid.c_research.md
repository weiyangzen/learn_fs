# File Research: sources/virtualization/open-iscsi/usr/iscsid.c

## Purpose
`iscsid.c` implements the long-running open-iscsi initiator daemon. It owns daemon startup, logging, privilege setup, management IPC listener setup, kernel netlink control-device access, initiator configuration, stale session synchronization, discovery daemon startup, memory/resource hardening, systemd readiness notification, event loop execution, and shutdown cleanup.

## Startup Flow
`main()` parses config, initiator name file, foreground/debug/user/group/pid options, validates conflicting PID options, initializes logging, signal handling, sysfs, IDBM, and management IPC. In daemon mode it opens and locks the PID file, forks, writes the child PID, opens the kernel control device, and daemonizes. It can then drop group memberships, set gid/uid, read `InitiatorName` and optional `InitiatorAlias`, set safe logout and IPC auth mode, and count pre-existing sysfs sessions.

## Session Recovery
If sessions already exist, the daemon forks a recovery child that iterates sessions and calls `sync_session()`. `sync_session()` maps a sysfs session back to a node record, merges negotiated/sysfs values and database values, skips firmware DB sessions after optional host scan, and sends `MGMT_IPC_SESSION_SYNC` to the daemon IPC path with retries while the daemon comes up.

## Runtime and Shutdown
After recovery setup, `main()` initializes the initiator, raises file limits, starts discoveryd, adjusts OOM score, locks memory with `mlockall()`, marks the daemon as an IO flusher when supported, notifies systemd readiness, and enters `event_loop(ipc, control_fd, mgmt_ipc_fd)`. Shutdown terminates IDBM/sysfs/IPC resources, frees initiator state and config strings, closes control and management IPC, and stops the logging daemon.

## Dependencies and Integration
The daemon integrates `mgmt_ipc`, `event_poll`, `iscsi_ipc`, `initiator`, `transport`, `idbm`, `iscsi_sysfs`, `discoveryd`, `iscsid_req`, and optional systemd notification. The global `dconfig` from `iscsid.h` exposes config to other daemon modules.

## Risk Notes
- The daemon does privileged setup before optional uid/gid drop; failures generally exit immediately.
- `sync_session()` intentionally tolerates some mismatches and unavailable records to recover sessions created outside the current database.
- `mlockall()` failure is fatal, while OOM and IO-flusher setup failures are nonfatal warnings.
