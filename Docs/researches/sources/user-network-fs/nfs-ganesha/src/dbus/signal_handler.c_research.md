<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/signal_handler.c -->
## sources/user-network-fs/nfs-ganesha/src/dbus/signal_handler.c

Purpose: helper implementation for sending simple D-Bus signals.

Important APIs/functions: `dbus_append_signal_string()` appends a string payload to a signal iterator and returns `ENOMEM` on append failure. `dbus_send_signal()` creates a signal with object/interface/signal names, initializes an iterator, invokes a payload callback, sends the message, flushes the connection, and unrefs the message.

Control flow/state: only a static signal serial in `dbus_send_signal`. The caller controls connection lifetime, signal names, and payload construction through the callback.

Dependencies/integration: uses libdbus and the private header declarations. It is an older/general helper alongside the variadic `gsh_dbus_broadcast()` in `dbus_server.c`.

Risks: if the payload callback fails, `dbus_send_signal()` returns immediately without unrefing the allocated message, leaking it. A send failure also returns without unrefing. The helper assumes the payload callback appends exactly the signal signature clients expect.

Test signals: unit or integration tests should force payload failure and send failure to catch leaks, and validate a string payload signal on the system bus.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/dbus/signal_handler.c -->
