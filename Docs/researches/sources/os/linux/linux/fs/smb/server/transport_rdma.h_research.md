# File Research: sources/os/linux/linux/fs/smb/server/transport_rdma.h

Declares SMBDirect transport limits and RDMA lifecycle/query APIs.

Key contents:
- Default/min/max SMBDirect I/O sizes: 8 MiB default, 512 KiB minimum, 16 MiB maximum.
- When `CONFIG_SMB_SERVER_SMBDIRECT` is enabled, exports init, stop-listening, netdev capability, max I/O initialization, and active transport max read/write size helpers.
- When disabled, provides no-op or false/zero inline stubs.
- Includes public `<linux/smbdirect.h>`.

Role in subsystem:
- Lets core ksmbd code call RDMA support conditionally without scattering config guards.
