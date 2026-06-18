<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/wscript_build -->
# sources/user-network-fs/samba/source4/auth/ntlm/wscript_build

Purpose: Waf build declarations for auth4 NTLM backends, core auth4 library, and service initializer.

Important build targets: modules include `auth4_sam_module`, `auth4_anonymous`, `auth4_winbind`, `auth4_developer`, and internal service module `service_auth`. The private library `auth4` builds `auth.c`, `auth_util.c`, and `auth_simple.c` with generated `auth_proto.h`. `auth4_sam_module` is AD DC gated; `auth4_developer` is developer-mode gated.

Control flow and state: build declarations determine which backends are compiled and registered through `STATIC_auth4_MODULES`. Runtime method availability depends on these targets and configuration gates.

Dependencies and integration: links SAM backend to samdb, NTLMSSP common code, hostconfig, IRPC/messaging, db glue, and authn policy utilities. Winbind backend links generated winbind RPC, messaging, and wbclient. Core auth4 links Samba security, credentials, tevent, old wbclient, Unix token, modules, and Kerberos utilities.

Risks and test signals: test AD DC enabled/disabled, developer-mode enabled/disabled, static module registration, generated prototype coverage, and service module initialization. Dependency omissions here surface as missing backends, unresolved authn policy symbols, or failed LDAP simple bind/session generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/wscript_build -->
