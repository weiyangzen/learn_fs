<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_heartbeat.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/dbus_heartbeat.c

Purpose: periodic D-Bus heartbeat broadcaster for daemon health.

Important APIs/functions: `dbus_heartbeat_cb(void *arg)` calls `nfs_health()` and, when healthy, emits a D-Bus boolean signal via `gsh_dbus_broadcast(DBUS_PATH HEARTBEAT_NAME, DBUS_ADMIN_IFACE, HEARTBEAT_NAME, ...)`. `init_heartbeat()` registers the callback through `add_dbus_broadcast`.

Control flow/state: heartbeat scheduling is delegated to the D-Bus broadcast loop. The callback returns `BCAST_STATUS_OK` on success, `BCAST_STATUS_WARN` if broadcasting fails, and suppresses signal emission when `nfs_health()` is false. Interval state is stored in the broadcast item created from `nfs_param.core_param.heartbeat_freq * NS_PER_MSEC`.

Dependencies/integration: depends on `nfs_health`, `gsh_dbus_broadcast`, D-Bus names/macros from `gsh_dbus.h`, and core parameter configuration. Integrated by `init_dbus_broadcast()` when heartbeat frequency is positive.

Risks: a failed D-Bus connection degrades to warning return but does not itself stop the daemon. The interval conversion assumes heartbeat frequency units match milliseconds. No unhealthy signal is sent, so listeners infer failure from missing heartbeats.

Test signals: set a positive heartbeat frequency, monitor the system bus for heartbeat signals while healthy, then force broadcast failure or health failure and check logging/absence behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_heartbeat.c -->
