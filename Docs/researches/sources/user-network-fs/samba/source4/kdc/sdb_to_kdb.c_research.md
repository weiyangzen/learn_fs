# sources/user-network-fs/samba/source4/kdc/sdb_to_kdb.c

## Purpose

`sdb_to_kdb.c` converts Samba's internal Kerberos `struct sdb_entry` into MIT Kerberos `krb5_db_entry` records. It exposes Samba-backed principals, flags, key material, salts, validity windows, and the private `samba_kdc_entry` pointer to MIT KDB consumers.

## Important APIs, Types, and Functions

The exported API is `sdb_entry_to_krb5_db_entry()`. Helpers map `SDBFlags` to `KRB5_KDB_*` attributes, copy created/modified event data via `krb5_dbe_update_mod_princ_data()`, translate SDB salts and keys into `krb5_key_data`, and clean partially built entries with `free_krb5_db_entry()`.

## Control Flow

The converter zeroes the output, sets KDB magic/length, copies the principal, maps flags, copies max life/renewal/expiration fields, writes modifier metadata when available, and copies all keys unless `require_hwauth` is set. Any failed Kerberos or allocation step unwinds through the local free helper. On success, `k->e_data` is set to the borrowed `samba_kdc_entry`, and that entry receives a back pointer to the KDB entry.

## State and Persistence Behavior

No database writes happen here. The file allocates MIT KDB entry buffers and copies secret key data into them; the cleanup path burns key buffers before free. The `samba_kdc_entry` stored in `e_data` is not owned by the MIT entry, so caller lifetime matters.

## Dependencies and Integration Points

It depends on MIT `kdb.h`, Samba SDB/KDB headers, `kdc/samba_kdc.h`, and Kerberos wrapper macros. It is built as the `sdb_kdb` subsystem when `HAVE_KDB_H` is available and feeds MIT KDC integration targets declared in the KDC build script.

## Risks and Edge Cases

Salt handling uses special salts outside disabled code. `require_hwauth` intentionally suppresses password keys. A `malloc()` failure for the key-data array returns the previous `ret` value, which may still be zero, so that branch deserves review. The private back pointer is lifetime-sensitive.

## Test Signals

Test entries should cover multiple keys, salts, `require_hwauth`, disabled/invalid flags, password expiry, minimal realm lookup entries, allocation-failure cleanup, and key-buffer scrubbing.
