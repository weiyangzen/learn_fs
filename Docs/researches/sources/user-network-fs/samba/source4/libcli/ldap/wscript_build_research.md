# sources/user-network-fs/samba/source4/libcli/ldap/wscript_build

Purpose: Waf build definition for the private Samba `cli-ldap` library.

Important configuration: builds `ldap_client.c`, `ldap_bind.c`, `ldap_ildap.c`, and `ldap_controls.c`; generates `ldap_proto.h`; exposes `samba-errors` and `tevent` public dependencies; declares private headers `libcli_ldap.h:ldap-util.h`; links against composite, LDB, tsocket, socket, SAMR NDR, TLS, generic NDR, loadparm/resolve, GENSEC, and common LDAP client helpers; marks the library private.

Control flow and state: no runtime behavior. It controls compile/link integration and generated prototypes.

Dependencies and integration: this file is the build-level connection between LDAP client code and the broader Samba libraries needed for TLS, GENSEC, resolver, and ASN.1/NDR support.

Risks: missing dependencies appear as compile or link failures, especially for TLS/GENSEC/control codecs. Test signals include clean Waf configure/build for `cli-ldap`, generated `ldap_proto.h` freshness, and dependent subsystem link tests.
