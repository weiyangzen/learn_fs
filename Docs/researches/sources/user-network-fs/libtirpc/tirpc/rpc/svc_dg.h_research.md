# sources/user-network-fs/libtirpc/tirpc/rpc/svc_dg.h

Purpose: `svc_dg.h` exposes internal datagram service transport state needed by rpcbind code.

Important APIs, types, and functions: It defines `struct svc_dg_data` with IO size, XID, XDR handle, verifier storage, duplicate request cache, received `msghdr`, control-message buffer, and macro `__rpcb_get_dg_xidp`.

Control flow: Datagram transport code stores per-request decode/reply state in `xp_p2`; rpcbind can access the current XID pointer through the macro.

State and persistence behavior: Instances are kept in `SVCXPRT->xp_p2` and persist for the datagram transport lifetime. The cache pointer may hold duplicate-request cache state.

Dependencies and integration points: It depends on `XDR`, `MAX_AUTH_BYTES`, `struct msghdr`, and the service transport private-slot convention. Comments restrict intended includes to `svc_dg.c` and rpcbind shared service code.

Risks: This is an internal layout exposed for rpcbind coupling; changing field order can break code such as `ti_opts.c` that expects `su_iosz` first. Fixed `su_cmsg[64]` may be insufficient for some ancillary data extensions.

Test signals: Tests should cover datagram request decode/reply, XID access by rpcbind, duplicate cache behavior, ancillary control-message handling, and ABI-sensitive field layout if external code depends on it.
