## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.h

Purpose: private interface shared by the MIT KDB plugin implementation files.

Important APIs and types: declares context helpers (`ks_get_context`), principal wrappers/free routines, kadmin principal classifiers, DAL methods for get/put/delete/iterate, master-key functions, encrypt/decrypt key-data shims, PAC/policy/delegation hooks, audit hook, and `kdb_samba_change_pwd()`. Defines `PAC_LOGON_INFO` and a portability `discard_const_p` macro.

Control flow and integration: this header mirrors the function table in `kdb_samba.c`, allowing each KDB operation to live in a focused implementation file while satisfying MIT KDB DAL signatures.

State and persistence: no state directly; most declarations accept `krb5_context`, from which `ks_get_context()` recovers the `mit_samba_context` tied to DSDB.

Dependencies: MIT krb5 plugin/KDB headers, Samba `mit_samba_context`, and KDC/PAC abstractions.

Risks: MIT KDB signatures vary across versions; this header is the compatibility choke point. `discard_const_p` can hide const ownership issues and should stay constrained.

Test signals: compile against supported MIT versions with `HAVE_KDB_H`, and verify every function table member has a matching prototype.
