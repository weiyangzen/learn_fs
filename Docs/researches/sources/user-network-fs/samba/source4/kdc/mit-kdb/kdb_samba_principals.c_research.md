## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_principals.c

Purpose: principal fetch, fake administrative principal creation, principal freeing, and iteration for the MIT KDB plugin.

Important APIs and functions: `ks_get_principal()` delegates to `mit_samba_get_principal()`. `ks_free_principal()` frees MIT principal entries, tl-data, key data with zeroing, and attached `samba_kdc_entry`. `ks_get_master_key_principal()` returns a disabled dummy K/M entry. `ks_create_principal()` synthesizes temporary principals with random salt/password-derived AES256 keys. `ks_get_admin_principal()` creates fake `kadmin/admin` and `kadmin/history` entries. `kdb_samba_db_get_principal()` handles special principals, marks `kadmin/changepw` with `KRB5_KDB_PWCHANGE_SERVICE` and short lifetime, and otherwise fetches from DSDB. Put returns success without storing; delete returns database-in-use; iterate walks Samba keys.

Control flow: special MIT/kadmin principals are intercepted before DSDB lookup. Iteration calls the supplied callback for each converted DSDB entry until callback error or no-entry.

State and persistence: real entries are transient MIT wrappers around DSDB records. Synthetic admin/master principals are in-memory only. Put/delete do not mutate DSDB.

Dependencies and integration: depends on `mit_samba_get_principal()`, generated random password/salt helpers, MIT krb5 key derivation, and `samba_kdc_entry` lifetime rules.

Risks: a bug in free logic can leak or double-free attached Samba entry contexts. Synthetic admin principals must be sufficient for kadmind startup without granting unintended ticket use. Put returning success may hide unsupported write operations after password changes.

Test signals: lookup of K/M, kadmin/admin/history/changepw, normal user/server/krbtgt principals, key zeroing on free, iterator callback errors, and unsupported put/delete semantics.
