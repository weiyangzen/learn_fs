# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_mountrpc.c

This file implements minimal kernel RPC helpers for diskless NFS root and BOOTP bootstrapping. It is compiled only under `BOOTP` or `NFS_ROOT`; normal mounts are expected to use the richer userland mount implementation.

Primary responsibilities:
- Parse boot-time NFS mount options.
- Contact mountd through portmap to obtain a root file handle.
- Resolve a swap file under the mounted export.
- Parse simple `server:path` boot strings.
- Decode small XDR values from mbuf chains.

Key functions:
- `nfs_mountopts()` initializes default `nfs_args` for diskless mounts: 8 KiB read/write size, reserved port, stream socket, and optional `rsize=`, `wsize=`, `intr`, `soft`, `noconn`, `udp`.
- `md_mount()` first tries MOUNT protocol v3, falls back to v1/v2-style mount, validates returned file handle size, checks v3 auth flavors for `RPCAUTH_UNIX`, then resolves the NFS service port.
- `md_lookup_swap()` performs an NFS LOOKUP for a swap path, decodes returned file handle and attributes, and sets `nfsv3_diskless.swap_nblks` from file size when unset.
- `setfs()` parses dotted IPv4 plus colon-separated path into `sockaddr_in` and mount path storage.
- `getdec()`, `substr()`, `xdr_opaque_decode()`, and `xdr_int_decode()` are local parsing helpers.

Important interactions:
- Uses `krpc_portmap()` and `krpc_call()` rather than the general NFS client request state machine.
- Builds small XDR requests with `xdr_string_encode()` and manual mbuf allocation.
- Shares protocol constants with `rpcv2.h`, `nfsproto.h`, and `nfsmountrpc.h`.

Caveats:
- This is bootstrapping code, not general-purpose mount RPC logic.
- `setfs()` only parses numeric IPv4 addresses.
- XDR decode helpers require contiguous/pullup-able mbuf data and return `EBADRPC` on malformed replies.
