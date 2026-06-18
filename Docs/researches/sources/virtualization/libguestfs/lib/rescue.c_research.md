# File Research: sources/virtualization/libguestfs/lib/rescue.c

Support helper for `virt-rescue`.

Important behavior:
- `guestfs_impl_internal_get_console_socket` requires a launched handle with an active connection.
- Verifies the connection class supports `get_console_sock`.
- Returns the connection’s console socket descriptor or a not-supported error.

Filesystem relevance:
- Exposes the appliance console for rescue workflows where users interact with the mounted/available guest environment.
