# File Research: sources/os/linux/linux-stable/fs/afs/Kconfig

This file defines kernel configuration options for the Linux AFS client.

Configuration entries:
- `AFS_FS` is a tristate Andrew File System client option depending on `INET`.
- `AFS_FS` selects `AF_RXRPC`, `DNS_RESOLVER`, `NETFS_SUPPORT`, and `CRYPTO_KRB5`.
- Help text describes the client as experimental and historically read-only/unsecured in the visible prompt text.
- `AFS_DEBUG` enables runtime-controllable debugging messages for the AFS client.
- `AFS_FSCACHE` enables local caching through the generic filesystem cache manager when AFS and FSCACHE linkage modes are compatible.
- `AFS_DEBUG_CURSOR` enables server cursor debugging dumps when server rotation fails.

Build implications:
- Enabling `AFS_FS` pulls in the RxRPC transport and DNS resolver support required by the implementation files in this group.
- `AFS_FSCACHE` gates integration with fscache usage visible in directory and vnode data paths.
