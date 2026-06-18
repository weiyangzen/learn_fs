# File Research: sources/virtualization/libguestfs/lib/conn-socket.c

## Role
Implements the POSIX socket transport between the host library and the guestfs daemon/appliance console.

## Connection Modes
- `guestfs_int_new_conn_socket_listening()` owns a listening daemon socket and optional console socket, then waits for the daemon to connect.
- `guestfs_int_new_conn_socket_connected()` wraps an already connected daemon socket.
- Sockets are set nonblocking.

## Operations
- `accept_connection()` polls daemon and console sockets until the daemon connects or appliance timeout expires.
- `read_data()` and `write_data()` poll daemon data readiness while also draining console logs.
- `can_read_data()` performs nonblocking readiness polling.
- `get_console_sock()` exposes the console socket when present.
- `free_conn_socket()` closes all owned sockets.

## Console Handling
`handle_log_message()` reads appliance console output, emits log callbacks, and responds to SGABIOS serial-console Device Status Report queries with a fake 24x80 response to avoid boot delays.

## Filesystem/Storage Relevance
All daemon filesystem and block-device RPC traffic passes through this connection implementation for direct socket-based launches.
