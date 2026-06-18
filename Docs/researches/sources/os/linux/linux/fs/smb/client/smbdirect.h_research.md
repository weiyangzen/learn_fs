# File Research: sources/os/linux/linux/fs/smb/client/smbdirect.h

## Purpose

`smbdirect.h` declares the CIFS SMB Direct transport interface and provides no-op fallback stubs when SMB Direct support is not compiled.

## Main Contents

- `cifs_rdma_enabled(server)` macro, either `server->rdma` or constant `0`.
- Extern declarations for SMB Direct tunables such as credit limits, send/receive sizes, keepalive interval, FRMR depth, and RDMA threshold.
- `struct smbd_connection`, which currently wraps a `struct smbdirect_socket *`.
- Declarations for connection lifecycle: `smbd_get_connection()`, `smbd_reconnect()`, `smbd_destroy()`.
- Declarations for send/receive: `smbd_recv()` and `smbd_send()`.
- Declarations for RDMA memory registration and buffer descriptor filling.
- Debug output declaration: `smbd_debug_proc_show()`.
- Fallback stubs returning `NULL` or `-1` when `CONFIG_CIFS_SMB_DIRECT` is disabled.

## Integration

- Included by `smb2pdu.c` and transport/session code that can optionally use RDMA.
- Pulls in `linux/smbdirect.h` only when SMB Direct is enabled.
- Allows most call sites to compile without conditional declarations, while implementation code still uses `#ifdef CONFIG_CIFS_SMB_DIRECT` for offload-only logic.

## Risk Notes

- Fallback stubs return generic `-1` rather than a specific errno, so callers should normally gate behavior through `cifs_rdma_enabled()` or config checks.
- The public structure is intentionally small; expanding it changes the abstraction boundary between CIFS and the SMB Direct socket layer.
