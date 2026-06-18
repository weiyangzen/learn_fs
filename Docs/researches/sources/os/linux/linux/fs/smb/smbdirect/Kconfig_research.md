# File Research: sources/os/linux/linux/fs/smb/smbdirect/Kconfig

Defines the `SMBDIRECT` kernel configuration option.

Key contents:
- `config SMBDIRECT` defaults to `n`.
- Depends on `INFINIBAND` and `INFINIBAND_ADDR_TRANS`.
- Requires module-compatible InfiniBand availability through `depends on m || INFINIBAND=y`.
- Selects `SG_POOL`.

Role in subsystem:
- Build-time gate for the common SMBDirect support module used by ksmbd RDMA transport.
