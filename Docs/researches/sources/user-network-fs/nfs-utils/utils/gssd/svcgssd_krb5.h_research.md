# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd_krb5.h

Purpose: this header exposes the server gssd Kerberos enctype limiter lifecycle.

Important APIs: `int svcgssd_limit_krb5_enctypes(void);` applies kernel/default enctype restrictions to the current acquired GSS credential, and `void svcgssd_free_enctypes(void);` clears cached parsed enctype data.

Control flow and integration: `svcgssd_proc.c` calls the limiter before `gss_accept_sec_context()`, while `svcgssd.c` calls the free routine during process shutdown. The header intentionally hides the procfs file name and caching details.

State and persistence: no state is declared here; the implementation owns process-global caches and reads kernel procfs capability state.

Dependencies: consumers include this after GSS credential setup code, but the header itself has no includes beyond its guard.

Risks and tests: callers must treat nonzero return from `svcgssd_limit_krb5_enctypes()` as fatal for the current upcall. Compile tests should cover configurations with and without `HAVE_SET_ALLOWABLE_ENCTYPES`; behavior tests should ensure shutdown can call `svcgssd_free_enctypes()` safely even if no parse succeeded.
