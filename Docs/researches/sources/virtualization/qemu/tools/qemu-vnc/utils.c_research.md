# File Research: sources/virtualization/qemu/tools/qemu-vnc/utils.c

## Purpose
Utility code for establishing peer-to-peer D-Bus connections over already-created file descriptors.

## Behavior
- `dbus_p2p_from_fd()` wraps an fd in `GSocket`, creates a `GSocketConnection`, and creates a `GDBusConnection` with client authentication and delayed message processing.
- Reports errors for socket wrapping, socket connection creation, and D-Bus connection creation.
- `p2p_server_setup_thread()` is the GLib thread entry point.
- `p2p_dbus_thread_new()` starts a thread named `p2p-server-setup` and passes the fd through.

## Integration
Used by display and audio listener registration code to accept the local end of socketpairs while QEMU connects over the other end.

## Filesystem/Storage Relevance
None directly. It is IPC helper code for virtualization UI.
