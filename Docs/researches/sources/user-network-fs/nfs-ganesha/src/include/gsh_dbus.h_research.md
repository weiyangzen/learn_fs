# sources/user-network-fs/nfs-ganesha/src/include/gsh_dbus.h

Purpose: This header defines Ganesha's low-level DBus service provider interface, introspection model, heartbeat, broadcast queue, and path registration helpers.

Important APIs/types/functions: Constants define the base object path and admin interface. Argument helper macros define common DBus signatures and terminators. `dbus_prop_access_t`, `struct gsh_dbus_prop`, `gsh_dbus_arg`, `gsh_dbus_method`, `gsh_dbus_signal`, and `gsh_dbus_interface` model introspection and dispatch. Broadcast support uses `dbus_bcast_callback` and `struct dbus_bcast_item`. Public functions include `add_dbus_broadcast`, `del_dbus_broadcast`, `init_heartbeat`, `gsh_dbus_pkginit`, `gsh_dbus_pkgshutdown`, `gsh_dbus_thread`, `gsh_dbus_register_path`, and `gsh_dbus_broadcast`.

Control flow: Packages register object paths with interface arrays. A DBus thread runs the loop, dispatches method callbacks, emits broadcasts, and sends periodic heartbeat when configured.

State and persistence: Runtime DBus state includes registered paths, scheduled broadcast items with next time/count/interval, and heartbeat health. There is no disk persistence in this header.

Dependencies and integration points: Depends on libdbus, logging, optional 9P types, and list utilities. Exposes admin/status/stats integration to external controllers and monitoring.

Risks: Variable argument broadcasting depends on matching DBus type signatures. Interface arrays are NULL terminated; missing terminators can overrun. Callback code must be thread-safe relative to the shared DBus loop.

Test signals: Register a path with properties/methods/signals, verify introspection, heartbeat, status replies, broadcast count/interval behavior, shutdown cleanup, and optional 9P argument parsing.
