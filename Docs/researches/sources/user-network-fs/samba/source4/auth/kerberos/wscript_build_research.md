<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/wscript_build -->
# sources/user-network-fs/samba/source4/auth/kerberos/wscript_build

Purpose: Waf build declarations for source4 Kerberos support.

Important build targets: `KRB_INIT_CTX` builds `krb5_init_context.c` with `gssapi`, `krb5samba`, `dbwrap`, and `samba-util`. Private library `authkrb5` builds `kerberos_pac.c`, generates `proto.h`, exposes public dependencies on generated PAC NDR, `krb5samba`, Samba sockets, and resolve code, and links packet/NDR/LDB/KRB5 PAC/error helpers. `KERBEROS_UTIL` builds `kerberos_util.c` with generated `kerberos_util.h` and credential/Kerberos dependencies. `KERBEROS_SRV_KEYTAB` builds `srv_keytab.c` with generated `kerberos_srv_keytab.h`.

Control flow and state: no runtime behavior; build-time configuration decides whether Kerberos code is compiled through `HAVE_KRB5` and related Samba feature macros in the C sources. The target graph controls availability for GENSEC Kerberos, KDC, keytab export, and authentication code.

Dependencies and integration: integrates `krb5_init_context.c`, `kerberos_pac.c`, `kerberos_util.c`, and `srv_keytab.c` into distinct build products used by GENSEC, KDC, auth, and keytab code. Header-only files such as `kerberos.h`, `kerberos_credentials.h`, and `krb5_init_context.h` are consumed by those compiled units rather than listed as sources here.

Risks and test signals: both MIT and Heimdal builds should verify this target pulls the correct compatibility dependencies. AD DC disabled builds, static builds, and generated-prototype cleanup are important signals because many consumers include `auth/kerberos/proto.h`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/wscript_build -->
