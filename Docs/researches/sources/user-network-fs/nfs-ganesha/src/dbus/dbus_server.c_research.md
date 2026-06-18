<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_server.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/dbus_server.c

Purpose: low-level D-Bus service framework for Ganesha object paths, method dispatch, introspection, broadcasts, heartbeat scheduling, and package lifecycle.

Important APIs/types/functions: singleton `thread_state` stores initialization, thread id, wait entry, system-bus connection, D-Bus error, serial, AVL callout registry, and flags. `gsh_dbus_pkginit()` connects to `DBUS_BUS_SYSTEM`, builds optional prefixed name for `org.ganesha.nfsd`, requests bus ownership, initializes broadcasts, and marks initialized. `gsh_dbus_register_path()` registers object paths under `DBUS_PATH`. `dbus_message_entrypoint()` handles Introspect, Properties, and registered interface methods. `gsh_dbus_thread()` runs broadcast callbacks and `dbus_connection_read_write_dispatch`. `gsh_dbus_pkgshutdown()` joins the thread, unregisters object paths, releases the bus name, and unrefs the connection.

Control flow/state: object path handlers are stored in an AVL tree keyed by full path. Broadcast items are kept in a sorted global list protected by `dbus_bcast_lock`; callbacks are rescheduled by interval/count or removed. The D-Bus loop polls every 100 ms and exits on shutdown flag or disconnect.

Dependencies/integration: uses libdbus, pthreads, Ganesha lists/AVL/time helpers, RCU registration, logging, core parameters, and D-Bus interface descriptors from `gsh_dbus.h`.

Risks: global singleton state limits multiple independent bus instances. Broadcast callbacks execute while the broadcast mutex is held, so slow callbacks can block list mutation. `gsh_dbus_pkgshutdown()` joins `gsh_dbus_thrid` even if startup/thread creation sequencing is wrong. Prefix validation only accepts one simple component before the default name.

Test signals: daemon startup on a system bus, introspection XML requests, method calls on registered paths, broadcast callback scheduling, heartbeat delivery, disconnect handling, and clean shutdown without leaked object paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/dbus_server.c -->
