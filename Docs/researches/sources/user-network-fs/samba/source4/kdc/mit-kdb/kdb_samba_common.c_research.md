## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_common.c

Purpose: common helpers for the MIT KDB plugin.

Important APIs and functions: `ks_get_context()` retrieves the `mit_samba_context` from MIT's krb5 DB context and resets `errno` for clearer com_err reporting. `ks_data_eq_string()` compares krb5 data components to C strings. `ks_is_kadmin()`, `ks_is_kadmin_history()`, `ks_is_kadmin_changepw()`, and `ks_is_kadmin_admin()` classify special kadmin principals by components.

Control flow: all classifiers are pure checks on principal component count and component bytes. Missing DB context returns NULL.

State and persistence: no persistence. `errno = 0` side effect is deliberate to avoid stale errno in MIT logging.

Dependencies and integration: used by principal lookup, policy checks, and the password-change service restriction logic.

Risks: exact component matching means realm is ignored by these helpers; callers must perform realm checks when needed, as AS policy does for changepw. Resetting global errno is unusual but scoped to the entry point.

Test signals: kadmin/admin, kadmin/history, kadmin/changepw, bare kadmin, different component counts, and empty krb5 data.
