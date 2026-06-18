## sources/user-network-fs/samba/source4/kdc/mit-kdb/wscript_build

Purpose: Waf build definition for the MIT Kerberos KDB Samba plugin library.

Important build API: `bld.SAMBA_LIBRARY('mit-kdb-samba', ...)` compiles the MIT KDB implementation files into a private library with real name `samba.so`, installs it to `${LIBDIR}/krb5/plugins/kdb`, links `MIT_SAMBA`, `com_err`, `krb5`, and `kdb5`, and enables it only when `HAVE_KDB_H` is configured.

Control flow: the source list matches the plugin function table decomposition: module entry, common helpers, master-key shim, key-data shim, policies, principals, and password change.

State and persistence: build metadata only; no runtime state.

Dependencies and integration: bridges Samba's build system with MIT Kerberos plugin discovery expectations. The `realname='samba.so'` value is what MIT KDB loads by plugin name.

Risks: missing or reordered source files can create unresolved function table references. Incorrect install path or realname breaks runtime plugin loading. `HAVE_KDB_H` must accurately reflect MIT KDB development headers.

Test signals: configure with/without MIT KDB headers, inspect installed plugin path/name, and run MIT KDC startup using Samba KDB.
