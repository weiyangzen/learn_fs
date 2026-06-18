## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba.c

Purpose: MIT Kerberos KDB DAL plugin entry point for Samba. It registers the `kdb_function_table` that lets the MIT KDC/kadmind fetch principals, issue PACs, check policy, and change passwords backed by Samba DSDB.

Important APIs and functions: `kdb_samba_init_module()` creates `mit_samba_context` and stores it with `krb5_db_set_context()`. `kdb_samba_fini_module()` retrieves and frees it. Create/destroy return unsupported for kadmin database creation, lock/unlock are no-ops, and `get_age()` returns `time(NULL)`. `kdb_samba_db_free_principal_e_data()` frees the attached `samba_kdc_entry`.

Control flow: MIT calls through `kdb_function_table`, which delegates nearly all real operations to sibling files: principal fetch/iteration, master key shim, key data copy, AS policy/audit, delegation, PAC issue, and password change.

State and persistence: the module context owns Samba loadparm/event/DSDB state via `mit_samba_context`. Persistent data remains in DSDB; the plugin does not implement native MIT database storage.

Dependencies and integration: depends on MIT `<kdb.h>`, Samba `mit_samba`, and `samba_kdc` structures. Installed as `samba.so` under MIT KDB plugin path by `wscript_build`.

Risks: no locking or age tracking means MIT lookaside/cache semantics rely on current-time invalidation rather than real DSDB modification stamps. Unsupported create/destroy/put/delete must remain compatible with kadmin expectations.

Test signals: plugin load/unload, repeated init/fini, principal lookup through MIT KDC, kadmind startup with fake admin principals, and memory ownership of `e_data`.
