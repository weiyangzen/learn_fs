# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfscl.h

This header contains small NFS client-side definitions for NFSv4 nodes, request startup, renew timing, setattr behavior, and debug output.

Key contents:
- Defines `struct nfsv4node`, a variable-length record storing an NFSv4 file handle followed by a file name.
- `NFS4NODENAME()` returns the name pointer after the stored file handle.
- `NFSCL_REQSTART()` wraps `nfscl_reqstart()` using vnode-derived mount and file handle data.
- `NFSCL_RENEW()` and `NFSCL_LEASE()` convert between lease durations and renew intervals using a simple half/double rule.
- Defines `NFSSATTR_*` flags for special setattr encoding.
- Defines `NFSCL_DEBUG()` gated by `nfscl_debuglevel`.

Important dependencies:
- Used by client RPC and state code.
- Assumes `VFSTONFS`, `VTONFS`, and `nfscl_reqstart()` are available from surrounding client headers.

Risks and notes:
- The variable-length `nfsv4node` layout requires careful allocation size calculation by callers.
