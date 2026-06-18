# File Research: sources/os/linux/linux/fs/smb/server/Kconfig

This Kconfig file declares kernel configuration options for the KSMBD SMB3 server.

Key options:
- `SMB_SERVER`: tristate SMB3 server support. Depends on networking, multiuser, and file locking; selects NLS, UTF-8/UCS2 helpers, crypto primitives, AEAD CCM/GCM, ASN.1, OID registry, and CRC32.
- `SMB_SERVER_SMBDIRECT`: optional SMB Direct/RDMA support, dependent on InfiniBand support and module/static compatibility.
- `SMB_SERVER_CHECK_CAP_NET_ADMIN`: defaults on; prevents unprivileged processes from starting the server.
- `SMB_SERVER_KERBEROS5`: optional Kerberos 5 support, defaults on when SMB server is enabled.

The help text positions KSMBD as an SMB3 kernel server backed by `ksmbd-tools` userspace configuration and IPC.
