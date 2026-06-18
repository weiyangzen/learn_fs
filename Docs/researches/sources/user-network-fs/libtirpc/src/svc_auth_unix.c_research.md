<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_unix.c -->
# sources/user-network-fs/libtirpc/src/svc_auth_unix.c

Purpose: server-side AUTH_SYS/AUTH_UNIX credential decoder and AUTH_SHORT rejection.

Important APIs and functions: `_svcauth_unix()` decodes long-form Unix credentials into `struct authunix_parms` stored in `rqst->rq_clntcred`. `_svcauth_short()` rejects shorthand credentials with `AUTH_REJECTEDCRED`.

Control flow: `_svcauth_unix()` builds an XDR memory decoder over the raw credential, points output fields into the caller-provided credential area, and first tries an inline parse of timestamp, machine name, uid, gid, group count, and group list. It bounds machine name to `MAX_MACHINE_NAME`, group count to `NGRPS`, and validates the encoded credential length. If inline data is unavailable, it falls back to `xdr_authunix_parms`. It copies a non-empty incoming verifier into the transport reply verifier or emits AUTH_NULL otherwise.

State and persistence: no global state. Parsed credential storage is request-scoped and lives in the stack-backed area prepared by `svc_getreq_common()`.

Dependencies and integration points: called from `svc_auth.c` for `AUTH_SYS`; service dispatchers can read `rqst->rq_clntcred` as `authunix_parms`. Uses XDR and IXDR macros.

Risks: inline parser depends on sufficient raw credential length; it validates minimum size after reading fields, so malformed short buffers need fuzz coverage. AUTH_SYS is unauthenticated identity assertion and should not be treated as strong security. The debug `printf` on bad length writes to stdout.

Test signals: valid AUTH_SYS with zero and multiple groups, max machine name, overlong machine name, overlarge group count, short/truncated credential, fallback XDR path, verifier propagation, and AUTH_SHORT rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_unix.c -->
