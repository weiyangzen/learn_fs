# File Research: sources/os/linux/linux-stable/fs/smb/server/server.h

This header defines global ksmbd server state/configuration and declares server configuration/control APIs.

Enums:
- Server state:
  - `SERVER_STATE_STARTING_UP`
  - `SERVER_STATE_RUNNING`
  - `SERVER_STATE_RESETTING`
  - `SERVER_STATE_SHUTTING_DOWN`
- Config string slots:
  - `SERVER_CONF_NETBIOS_NAME`
  - `SERVER_CONF_SERVER_STRING`
  - `SERVER_CONF_WORK_GROUP`

Structure:
- `struct ksmbd_server_config`
  - Global feature flags and server state.
  - Signing policy.
  - Min/max protocol.
  - TCP port.
  - IPC timeout/activity.
  - Deadtime.
  - Fake filesystem capabilities for shares.
  - Domain SID.
  - Authentication mechanisms.
  - Connection and request limits.
  - Config strings.
  - Durable-handle scavenger task.
  - Bind-interface-only flag.

Global:
- `extern struct ksmbd_server_config server_conf`.

Declared APIs:
- String setters/getters:
  - `ksmbd_set_netbios_name()`
  - `ksmbd_set_server_string()`
  - `ksmbd_set_work_group()`
  - `ksmbd_netbios_name()`
  - `ksmbd_server_string()`
  - `ksmbd_work_group()`
- State helpers:
  - `ksmbd_server_running()`
  - `ksmbd_server_configurable()`
- Control work:
  - `server_queue_ctrl_init_work()`
  - `server_queue_ctrl_reset_work()`

Role:
- Shared server-global contract for transport IPC, request dispatch, proc reporting, sysfs control, and dialect initialization.

Risk areas:
- `server_conf` is global mutable state; users rely on `READ_ONCE()` state checks but most other fields are accessed directly.
- `ksmbd_server_configurable()` allows configuration before resetting or shutdown; callers must respect this gate.
