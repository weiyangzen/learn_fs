# sources/user-network-fs/samba/source4/libnet/libnet_export_keytab.c

## Purpose
`libnet_export_keytab.c` exports Kerberos keys from Samba's KDC database view into a keytab. It supports exporting all principals or a single principal, retaining or removing stale keytab entries, including only current or also historic keys, and gMSA key generation when direct key material is unavailable.

## Important APIs, Types, And Functions
The public API is `libnet_export_keytab()`. It initializes a Kerberos context, builds a Samba KDC base/db context from the libnet context and optional caller-provided `samdb`, chooses SDB flags, validates safe complete-keytab export behavior, and calls `sdb_kt_copy()`.

`sdb_kt_copy()` opens the target keytab for writing, fetches either one principal (`samba_kdc_fetch`) or iterates the KDC DB (`samba_kdc_firstkey`/`samba_kdc_nextkey`), optionally removes obsolete keytab entries, exports current and optionally old/older keysets, and handles gMSA key material through `smb_krb5_fill_keytab_gmsa_keys()`.

## Control Flow
For a single principal, the code parses the Kerberos principal name, fetches any matching SDB entry with `SDB_F_GET_ANY | sdb_flags`, exports its keys, and stops after one record. For full export, it iterates all KDC entries. Before a full export with stale-entry removal disabled, it refuses to write over an existing keytab file; if the file does not exist, stale retention is forced because there are no old entries to remove.

Each SDB entry is processed in a temporary talloc context. If stale entries should be removed, `smb_krb5_remove_obsolete_keytab_entries()` removes entries for that principal that do not match the current KVNO. For gMSA entries with no direct keys, the code generates keytab entries from gMSA password material and can treat missing user keys as non-fatal during full export. For normal entries, it checks whether each exact keytab entry already exists before adding it. Historic key export writes current keys at `kvno`, old keys at `kvno - 1`, and older keys at `kvno - 2`.

## State And Persistence Behavior
The persistent side effect is modification of the keytab named by `r->in.keytab_name`. When `keep_stale_entries` is false, obsolete keytab entries for exported principals may be removed. Complete export has a guard against overwriting an existing keytab unless stale entries are kept. The function reads KDC state from the configured Samba KDC DB context and may rely on current time for gMSA key validity.

## Dependencies And Integration Points
Dependencies include Samba Kerberos helpers, KDC DB glue/SDB iteration, gMSA utilities, Heimdal/MIT krb5 keytab APIs, `smb_krb5_*` keytab utilities, `samba_kdc_setup_db_ctx()`, and optional `samdb` with `DSDB_GMSA_TIME_OPAQUE`. The header `libnet_export_keytab.h` supplies the request structure.

## Risks
This path handles secret key material and writes keytabs, so permission, path, and overwrite behavior are security-sensitive. Full export without a local `samdb` can produce no keys except authorized gMSA cases; the error message explicitly calls this out. Historic KVNO handling assumes simple `kvno - 1` and `kvno - 2` mapping. Duplicate suppression depends on exact keytab-entry comparison. Failure paths preserve some detailed Kerberos errors but may return generic NT status codes.

## Test Signals
Tests should cover single-principal export, full export refusing existing files when stale entries would be removed, duplicate suppression, stale-entry cleanup, current-only vs historic-key export, gMSA export with/without authorization, missing key behavior with `keep_stale_entries`, and propagation of krb5 parse/open/add errors. Security tests should verify file overwrite and keytab path behavior.
