# File Research: sources/os/bsd/freebsd-src/sbin/mount_nfs/mount_nfs.c

## Summary
Mount helper for NFS. It parses NFS mount options, resolves servers, negotiates NFS and mount protocol details through RPC, obtains filehandles for NFSv2/v3, handles NFSv4 direct mounts, supports background retry behavior, and calls `nmount()`.

## Main Responsibilities
- Parses legacy flags and modern `-o` options for protocol, version, security, retry, sizes, timeout, locking, reserved ports, and background behavior.
- Loads `nfscl` if needed.
- Handles `server:path`, `[IPv6]:path`, and deprecated `path@server` syntax.
- Resolves hosts with IPv4/IPv6 filtering and TCP/UDP selection.
- For NFSv2/v3, contacts rpcbind and mountd, validates NFS null RPC, sends `MOUNTPROC_MNT`, and extracts root filehandle plus supported auth flavor.
- For NFSv4, skips mountd and passes server address, security flavor, `nfsv4`, and `dirpath`.
- Supports background retries and waits on routing-interface changes.
- Adds successful non-v4 mounts to `PATH_MOUNTTAB`.

## Key Functions
- `getnfsargs()`: parses remote spec, resolves address, retries protocol attempts.
- `nfs_tryproto()`: probes NFS service, mountd, filehandle/security negotiation, and iovec construction.
- `rtm_ifinfo_sleep()`: sleeps until network link state changes or timeout.
- `xdr_dir()` / `xdr_fh()`: mount protocol XDR handling.
- `sec_name_to_num()` / `sec_num_to_name()`.
- `netidbytype()` / `getnetconf_cached()`.

## Dependencies And Integration
Uses ONC RPC, rpcbind, mount protocol, NFS protocol headers, `nfsv4_geterrstr`, `build_iovec`, routing sockets, `nmount()`, and `mounttab` helpers.

## Research Notes
Security flavor negotiation is explicit for NFSv3 mountd responses: if a requested flavor is not advertised, the helper sets `EAUTH`. NFSv4 warns about `soft`/`intr` because they are unsafe for v4 semantics.
