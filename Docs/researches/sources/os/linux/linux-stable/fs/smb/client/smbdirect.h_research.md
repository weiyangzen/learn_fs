# File Research: sources/os/linux/linux-stable/fs/smb/client/smbdirect.h

## Summary
Declares the CIFS SMB Direct transport interface and compile-time stubs. When `CONFIG_CIFS_SMB_DIRECT` is enabled it exposes the RDMA connection wrapper, tunable globals, send/receive APIs, memory-registration APIs, and debug hook; otherwise it compiles callers against inert fallbacks.

## Main Responsibilities
- Define `cifs_rdma_enabled(server)` as either `server->rdma` or constant false depending on configuration.
- Include CIFS global structures and the kernel SMB Direct socket API for enabled builds.
- Declare SMB Direct module tunables shared with `smbdirect.c`.
- Define `struct smbd_connection` as a wrapper around `struct smbdirect_socket`.
- Declare connection lifecycle, transport I/O, RDMA memory registration, descriptor fill, deregistration, and debug functions.
- Provide disabled-build stubs for connection, reconnect, destroy, receive, and send operations.

## Key Interfaces
Enabled builds expose `smbd_get_connection()`, `smbd_get_parameters()`, `smbd_reconnect()`, `smbd_destroy()`, `smbd_recv()`, `smbd_send()`, `smbd_register_mr()`, `smbd_mr_fill_buffer_descriptor()`, `smbd_deregister_mr()`, and `smbd_debug_proc_show()`.

## Important Behavior
The disabled branch preserves a small subset of the call surface so generic CIFS code can compile without SMB Direct support. Some memory-registration declarations only exist in enabled builds, matching call sites that are themselves guarded by `CONFIG_CIFS_SMB_DIRECT`.

## Risks
Interface drift between the enabled declarations and disabled stubs can break non-RDMA builds. Callers must respect configuration guards around memory-registration helpers because the disabled branch does not define all RDMA types and functions.
