## sources/user-network-fs/samba/source4/kdc/mit_samba.c

Purpose: core bridge between MIT KDB callbacks and Samba's KDC/DSDB implementation. It creates runtime context, converts Samba SDB entries to MIT DB entries, handles PAC generation/update/delegation, checks client access, changes passwords, and updates bad-password accounting.

Important APIs and functions: `mit_samba_context_init/free()` set up tevent, loadparm, Samba KDC DB context, MIT krb5 context, and MIT log callback. `mit_samba_get_principal()` maps MIT KDB flags to SDB flags, fetches via `samba_kdc_fetch()`, handles wrong-realm referral principals, and converts via `sdb_entry_to_krb5_db_entry()`. `mit_samba_get_firstkey()/get_nextkey()` iterate DSDB. `mit_samba_get_pac()` calls `samba_kdc_get_pac()`. `mit_samba_update_pac()` verifies old PAC trust and calls `samba_kdc_update_pac()`. `mit_samba_check_client_access()`, `mit_samba_check_s4u2proxy()`, and `mit_samba_check_allowed_to_delegate_from()` bridge access and delegation policy. `mit_samba_kpasswd_change_password()` builds session info from DB user info and calls `samdb_kpasswd_change_password()`. `mit_samba_zero_bad_password_count()` and `mit_samba_update_bad_password_count()` persist logon accounting.

Control flow: principal lookup always forces canonicalization and requests admin data so `samba_kdc_entry` metadata is available. Wrong-realm TGS lookups retry as krbtgt referral lookups; wrong-realm AS TGT lookups let MIT return the client-facing error. PAC update checks krbtgt trust/in-DB state, validates the incoming PAC, maps MIT flags to Samba flags, and treats `ENOATTR` as no-PAC success for MIT.

State and persistence: `mit_samba_context` owns Samba DB context and MIT krb5 context. DSDB current time is refreshed before fetches and copied from entries before policy/PAC/accounting operations. Password and bad-password updates persist through SAMDB/auth_sam helpers.

Dependencies and integration: central integration point for MIT KDB DAL, `samba_kdc_fetch`, `sdb_to_kdb`, `pac-glue`, `db-glue`, `kpasswd_glue`, auth session generation, auth_sam accounting, and gMSA time handling.

Risks: context initialization must load the same smb.conf and DB context as the KDC. Referral retry logic can affect cross-realm ticketing. PAC trust handling for RODCs and cross-realm clients is security-sensitive. Password-change path expects UTF-8 MIT input and converts to UTF-16 for SAMDB.

Test signals: MIT KDC startup, client/server/krbtgt lookup flags, wrong-realm referral TGS, first/next iteration, AS/TGS PAC generation/update, protocol transition, constrained delegation, RBCD, kpasswd through kadmind, bad-password counter updates, and no-PAC accounts.
