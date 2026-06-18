<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_priv.h -->
## sources/user-network-fs/nfs-ganesha/src/dbus/dbus_priv.h

Purpose: private declarations shared by D-Bus implementation files.

Important API surface: declares `dbus_proc_property` for handling `org.freedesktop.DBus.Properties`; `dbus_append_signal_string` as a simple signal payload helper; and `dbus_send_signal` for constructing and sending a signal with a caller-provided payload callback.

Control flow/state: header only; no state. It establishes internal coupling between `dbus_server.c`, `properties_handler.c`, and `signal_handler.c`.

Dependencies/integration: relies on D-Bus C types (`DBusMessage`, `DBusMessageIter`, `DBusConnection`, `DBusError`) and Ganesha D-Bus interface structures. It is not a public admin API header; it supports the object path/message framework.

Risks: prototypes expose raw pointers and callback contracts without ownership annotations. Payload callbacks must append correct D-Bus types and handle iterator failures; callers must manage connection lifetime externally.

Test signals: compilation of all D-Bus sources is the primary signal. Runtime coverage comes from property Get/GetAll/Set calls and signal emission paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_priv.h -->
