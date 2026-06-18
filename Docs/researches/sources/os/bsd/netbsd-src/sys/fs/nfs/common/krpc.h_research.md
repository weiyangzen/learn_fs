# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc.h

## Purpose
Declares the minimal kernel SunRPC helper API used primarily by diskless NFS boot code.

## Interfaces
- `krpc_call`: performs a UDP RPC call to an IPv4 server and returns reply mbuf data.
- `krpc_portmap`: resolves an RPC program/version to a UDP port using portmapper.
- `xdr_string_encode`: creates an mbuf containing an XDR-counted padded string.
- Defines portmapper constants: fixed port 111, program/version, and procedures including `GETPORT`.

## Integration
Used by `bootp_subr.c` to contact mountd and resolve NFS/mountd ports while bootstrapping NFS root.

## Risks
Header prototypes mix `struct thread` forward declaration with `struct lwp *td` in the declarations, reflecting porting compatibility assumptions in this source tree.
