# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/rpcv2.h

This header defines SunRPC version 2 constants and authentication/GSS support values used by the NFS stack. It covers RPC versioning, auth flavors, AUTH_UNIX sizing, RPCSEC_GSS constants, gssd and nfsuserd private RPC program numbers, selected GSS major status codes, RPC reply/error constants, mount protocol constants, and a simple RPC time struct.

Key contents:
- RPC version constant `RPC_VER2`.
- Authentication flavors for null, UNIX, short, Kerberos, GSS, and Kerberos GSS service variants, plus max credential/verifier sizes.
- AUTH_UNIX minimum size and group count limit.
- RPCSEC_GSS version, procedure numbers, service types, sequence window constants, MIC/WRAP constants, QOP, and token/header sizing.
- Private RPC program definitions for `gssd` and `nfsuserd`, including procedure numbers for server and client credential/name operations.
- GSS major status constants guarded so they do not conflict with system GSS headers.
- Core RPC message, accept/deny, program/procedure, garbage, mismatch, and auth error constants.
- Authentication failure constants.
- RPC call/reply header sizes.
- Mount daemon program/version/procedure/path/name constants and NFS RPC program number.
- `struct rpcv2_time`.

Important behavior:
- This header supplies constants needed by both client/server NFS RPC and auxiliary daemons such as gssd and nfsuserd.
- The GSS status block is conditional to avoid redefining values when a GSSAPI header has already been included.

Research notes:
- Use this when tracing RPC header parsing, authentication flavor selection, mount protocol calls, or kernel-to-gssd/nfsuserd interactions.
- ABI-sensitive areas include auth flavor numeric values, RPC program numbers, and header size assumptions.
