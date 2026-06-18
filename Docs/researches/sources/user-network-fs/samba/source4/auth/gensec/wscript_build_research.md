<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/wscript_build -->
# sources/user-network-fs/samba/source4/auth/gensec/wscript_build

Purpose: Waf build declarations for source4 GENSEC support modules and Python bindings.

Important build targets: `gensec_util` builds `gensec_tstream.c` with `tevent-util`, `tevent`, `samba-util`, and `LIBTSOCKET`, producing `gensec_proto.h`. `gensec_krb5` chooses either `gensec_krb5_heimdal.c` or `gensec_krb5_mit.c` depending on `SAMBA_USES_MITKDC`, initializes with `gensec_krb5_init`, and is enabled for AD DC builds. `gensec_krb5_helpers` is also AD DC gated. `gensec_gssapi` builds the GSSAPI mechanism. `pygensec` builds `pygensec.c` as `samba/gensec.so` with pytalloc and pyparam helper libraries.

Control flow and state: no runtime control flow, but build-time feature selection decides which Kerberos implementation is compiled and whether AD DC-only helpers are available. The declarations feed Samba's module registration system through subsystem names, init functions, and internal/external module flags.

Dependencies and integration: integrates auth GENSEC with Samba credentials, authkrb5, GSSAPI, com_err, talloc, Python embedding, and host configuration. Build failures here usually appear as missing generated prototypes, unresolved module init functions, or Python extension load errors.

Risks and test signals: test both MIT and Heimdal configurations, AD DC enabled/disabled builds, static and shared module layouts, and Python import of `samba.gensec`. Dependency drift in pyembed library names or Kerberos config symbols can silently omit features from downstream tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/gensec/wscript_build -->
