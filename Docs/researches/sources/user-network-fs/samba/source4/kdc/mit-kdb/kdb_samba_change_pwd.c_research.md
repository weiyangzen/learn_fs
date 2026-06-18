## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_change_pwd.c

Purpose: MIT KDB DAL password-change hook that bridges MIT password-change requests into Samba's SAMDB-backed password-change implementation.

Important API: `kdb_samba_change_pwd()` retrieves `mit_samba_context` with `ks_get_context()` and calls `mit_samba_kpasswd_change_password(mit_ctx, passwd, db_entry)`. It ignores MIT master key, key salt tuple, kvno, and keepold inputs because Samba does not use MIT's local key database storage path for password changes.

Control flow: missing plugin context returns `KRB5_KDB_DBNOTINITED`; otherwise the helper result is returned directly.

State and persistence: persistence happens inside `mit_samba_kpasswd_change_password()`, which generates session information and writes to SAMDB. This file holds no durable state.

Dependencies and integration: registered as `.change_pwd` in `kdb_function_table`; depends on `mit_samba.c` and `kpasswd_glue.c` for the real work.

Risks: callers might expect MIT KDB key-generation parameters to be honored. Samba instead relies on DSDB password handling and policy, so divergence from MIT kadmind assumptions should be covered in tests.

Test signals: kadmind password change through the MIT plugin, missing context, policy rejection mapping to KADM5 errors, and verification that kvno/key history are updated by DSDB rather than this hook.
