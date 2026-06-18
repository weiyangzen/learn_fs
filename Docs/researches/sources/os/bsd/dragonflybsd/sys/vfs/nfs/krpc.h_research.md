# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc.h

## Role

Declares the small kernel SunRPC helper API used during NFS diskless boot and mountd/portmapper bootstrap work.

## API

- `krpc_call()` performs a UDP RPC call to an IPv4 server and returns the reply mbuf chain.
- `krpc_portmap()` asks portmapper for a program/version UDP port.
- `xdr_string_encode()` creates an mbuf containing an XDR string.

## Constants

Defines portmapper program, version, fixed port, and procedure numbers:

- `PMAPPORT`
- `PMAPPROG`
- `PMAPVERS`
- `PMAPPROC_NULL`
- `PMAPPROC_SET`
- `PMAPPROC_UNSET`
- `PMAPPROC_GETPORT`
- `PMAPPROC_DUMP`
- `PMAPPROC_CALLIT`

## Dependencies

Forward declares `mbuf`, `thread`, and socket address structures. The implementation lives in `krpc_subr.c`.

## Research Notes

The header is intentionally narrow and IPv4-specific. It is infrastructure for bootstrapping NFS-root support before higher-level NFS client machinery is available.
