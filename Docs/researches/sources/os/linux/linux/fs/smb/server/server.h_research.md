# File Research: sources/os/linux/linux/fs/smb/server/server.h

This header defines global ksmbd server state and configuration APIs.

Server states:
- Starting up
- Running
- Resetting
- Shutting down

Configuration:
- `struct ksmbd_server_config` stores global flags, state, signing policy, protocol range, TCP port, IPC timeout/activity, deadtime, fake filesystem capabilities, domain SID, auth mechanisms, connection/request limits, config strings, durable-handle task, and interface binding mode.
- Config string indexes cover NetBIOS name, server string, and workgroup.
- `server_conf` is exported globally.

Public helpers:
- Setters/getters for NetBIOS name, server string, and workgroup.
- `ksmbd_server_running()` checks for `SERVER_STATE_RUNNING` with `READ_ONCE`.
- `ksmbd_server_configurable()` permits configuration while state is before resetting.
- Control-work queue functions request server init or reset.

Role in this group:
- `server.c` owns the global object and lifecycle.
- `proc.c` reads this state for procfs stats.
- `smb2ops.c` reads flags/protocol capabilities while initializing per-connection SMB dialect operations.
