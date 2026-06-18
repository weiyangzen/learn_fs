<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos.h -->
# sources/user-network-fs/samba/source4/auth/kerberos/kerberos.h

Purpose: central source4 Kerberos public header gated by `HAVE_KRB5`. It collects Kerberos wrappers, containers, token identifiers, encryption masks, and PAC creation prototypes used by GENSEC, KDC, and authentication code.

Important APIs and types: `struct ccache_container` binds an `smb_krb5_context` to a `krb5_ccache`; `struct keytab_container` binds the context to a `krb5_keytab` and records whether it is password based. RFC 1964/GSS token IDs are defined for AP-REQ, AP-REP, KRB-ERROR, GETMIC, and WRAP. Encryption masks include `ENC_ALL_TYPES` and `ENC_STRONG_SALTED_TYPES`. Compatibility prototypes cover missing krb5 functions. Exports include `smb_krb5_princ_component()`, `kerberos_encode_pac()`, and `kerberos_create_pac()`.

Control flow and state: the header defines no execution but establishes ownership expectations: ccache/keytab wrappers carry the Kerberos context required for cleanup and operations. PAC APIs take explicit KDC and service keyblocks because PAC checksums have two signing roles.

Dependencies and integration: includes system Kerberos headers, Samba auth headers, `krb5_init_context.h`, generated PAC NDR structures, and Samba krb5 wrappers. It includes generated `auth/kerberos/proto.h`, so implementation exports are collected through autoproto.

Risks and test signals: compile coverage must exercise `HAVE_KRB5` on/off, MIT/Heimdal compatibility macros, and consumers that include this header without unnecessary krb5 exposure. Security tests should verify that encryption masks match supported AD policy behavior and that PAC creation callers provide the correct krbtgt and service keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/kerberos/kerberos.h -->
