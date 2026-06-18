# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.h

## Summary
Declares ksmbd SMB Direct server transport entry points and default/min/max RDMA I/O sizing.

## Main Responsibilities
- Define `SMBD_DEFAULT_IOSIZE`, `SMBD_MIN_IOSIZE`, and `SMBD_MAX_IOSIZE`.
- Expose RDMA init, listener stop, netdev capability, max I/O configuration, and negotiated max read/write size helpers when `CONFIG_SMB_SERVER_SMBDIRECT` is enabled.
- Provide no-op/false/zero stubs when SMB Direct server support is disabled.
- Include the common `linux/smbdirect.h` API.

## Risks
The enabled and disabled APIs must remain source-compatible so callers do not need conditional code. Size bounds must stay aligned with SMB Direct negotiation limits.
