# File Research: sources/os/linux/linux/fs/afs/Kconfig

Purpose: declares build-time configuration for the Linux AFS client.

Key entries:
- `AFS_FS`: tristate Andrew File System client, depends on `INET`, selects `AF_RXRPC`, `DNS_RESOLVER`, `NETFS_SUPPORT`, and `CRYPTO_KRB5`.
- `AFS_DEBUG`: optional dynamic debugging.
- `AFS_FSCACHE`: optional local caching through fscache, constrained by built-in/module compatibility.
- `AFS_DEBUG_CURSOR`: optional server cursor debug dumps.

Implementation notes:
- Help text still describes the driver as experimental and points to `Documentation/filesystems/afs.rst`.
- `AFS_FSCACHE` is a bool gated on both AFS and FSCACHE linkage mode.

Dependencies:
- Network, RxRPC, DNS resolver, netfs, Kerberos crypto, and optional fscache infrastructure.
