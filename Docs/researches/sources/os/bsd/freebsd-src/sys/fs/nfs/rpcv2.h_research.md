# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/rpcv2.h

`rpcv2.h` defines Sun RPC version 2 constants and NFS-adjacent RPC authentication, GSS, mount protocol, gssd, and nfsuserd values.

Key contents:
- Defines RPC version `RPC_VER2`.
- Defines authentication flavors: null, UNIX/AUTH_SYS, short, Kerberos v4, RPCSEC_GSS, and FreeBSD Kerberos GSS service pseudo-flavors for none/integrity/privacy.
- Defines auth/verifier size limits and AUTH_UNIX minimum size/gid count.
- Defines RPCSEC_GSS version, procedures, services, sequence limits/window sizes, MIC/WRAP identifiers, QOP, and GSS XDR size constants.
- Defines private RPC program/procedure values for `gssd` and `nfsuserd`.
- Provides GSS major status constants if GSS headers have not already defined them.
- Defines RPC message/reply statuses, accept/deny statuses, auth failure values, common RPC header sizes, MOUNT program values, and NFS RPC program number.
- Defines `struct rpcv2_time`.

Important integration points:
- `nfsproto.h` uses RPC error constants to build `NFSERR_RPCERR`-tagged synthetic NFS errors.
- This header supplies protocol constants used by both client and server RPC wrapping code.
- Conditional GSS status definitions avoid duplicate definition when full GSS/RPCSEC headers are present.

Research notes:
- The file is a compact compatibility/protocol-definition header for RPC pieces that NFS needs without depending entirely on userland RPC generated headers.
