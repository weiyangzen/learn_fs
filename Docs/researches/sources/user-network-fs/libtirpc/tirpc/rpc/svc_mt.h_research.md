# sources/user-network-fs/libtirpc/tirpc/rpc/svc_mt.h

Purpose: `svc_mt.h` defines multithread/service transport extension data stored in `SVCXPRT->xp_p3`.

Important APIs, types, and functions: It defines `SVCXPRT_EXT` with `flags` and embedded `SVCAUTH xp_auth`, macros `SVCEXT`, `SVC_XP_AUTH`, `svc_flags`, `version_keepquiet`, and flag `SVC_VERSQUIET`.

Control flow: Transport implementations allocate `SVCXPRT_EXT`, attach it to `xp_p3`, then service/auth code reads or writes flags and auth state through macros. Version mismatch response behavior checks `version_keepquiet`.

State and persistence behavior: Extension state persists for the transport lifetime and is freed with the transport. Auth private state may need flavor-specific destroy handling before freeing.

Dependencies and integration points: It depends on `SVCAUTH` from `svc_auth.h` and `SVCXPRT` from `svc.h`. `svc_vc.c` allocates and uses this extension for auth wrap/unwrap.

Risks: Macros assume `xp_p3` is non-null and correctly typed. Missing extension allocation will crash service paths. Flags are raw ints with no locking in the macro layer.

Test signals: Tests should cover extension allocation in every transport constructor, version quiet controls, auth wrap/unwrap storage, and destroy cleanup for auth private data.
