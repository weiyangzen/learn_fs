# sources/user-network-fs/nfs-utils/utils/mount/network.h

Purpose: declares shared network/protocol interfaces for NFS mount and unmount code.

Important APIs and types: `clnt_addr_t` pairs hostname pointer, IPv4 sockaddr, and RPC `pmap`. Constants define mount RPC send/receive buffer sizes and common timeouts. It declares probing, lookup, presentation, callback address, ping, local address checks, option-to-version/protocol parsing, statd startup, mountd client lifecycle, UMNT calls, and `nfs_umount_do_umnt()`.

Control flow and integration: `nfsmount.c`, `nfs4mount.c`, `nfsumount.c`, `mount_libmount.c`, `error.c`, and `configfile.c` use this contract. The header exposes both legacy IPv4 `clnt_addr_t` and sockaddr-generic APIs.

State and persistence: declares `extern const char *nfs_transport_opttbl[]`; no mutable state is owned in the header.

Dependencies: includes `rpc/pmap_prot.h`; some declarations depend on `dirpath` and `CLIENT` types supplied by RPC/NFS includes in consumers.

Risks and tests: APIs mix legacy and newer address handling, so callers must use matching sockaddr lengths. Test signals are compile coverage across all mount code and behavior tests for option parsing/probing through the exported functions.
