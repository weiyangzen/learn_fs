## sources/user-network-fs/libtirpc/src/authunix_prot.c

Purpose: Implements the XDR codec for legacy AUTH_UNIX/AUTH_SYS authentication parameters. The single exported routine, `xdr_authunix_parms(XDR *xdrs, struct authunix_parms *p)`, serializes or deserializes timestamp, machine name, uid, gid, and supplementary groups.

Important APIs and control flow: The function asserts non-null inputs, then chains `xdr_u_long`, `xdr_string`, `xdr_u_int`, and `xdr_array` calls. The group array is capped by `NGRPS` and uses `xdr_int` for each element. The function returns `TRUE` only if every XDR operation succeeds.

State and persistence: No persistent state is owned here. In decode/free modes, allocation and release behavior are delegated to XDR primitives, especially `xdr_string` and `xdr_array`.

Dependencies and integration: Depends on `<rpc/auth_unix.h>` and the common XDR runtime. It is exported in `libtirpc.map.in` and is consumed by AUTH_UNIX credential creation/validation paths.

Risks and test signals: Risks are bounded by the XDR length caps. Tests should round-trip AUTH_UNIX credentials, exercise `NGRPS` boundaries, and verify decode/free behavior under malformed lengths and null-assert builds.
