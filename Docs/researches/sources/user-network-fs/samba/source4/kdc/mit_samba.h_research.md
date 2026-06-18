## sources/user-network-fs/samba/source4/kdc/mit_samba.h

Purpose: public interface for the MIT-Samba bridge library consumed by the MIT KDB plugin.

Important types and APIs: `struct mit_samba_context` stores optional session info, an MIT krb5 context, and a `samba_kdc_db_context`. Function declarations cover context lifecycle, salt/password generation, principal fetch/iteration, PAC get/update/reget, client access checks, S4U2Proxy/RBCD checks, kpasswd password change, bad-password accounting, and PAC requirement checks.

Control flow and integration: this header is the stable boundary between `mit-kdb/*` plugin code and the larger Samba KDC implementation in `mit_samba.c`/`pac-glue.c`.

State and persistence: context points to DSDB-backed KDC state; callers must treat returned MIT DB entries as transient wrappers and free them through KDB hooks.

Dependencies: requires krb5 types, `krb5_db_entry`, `krb5_pac`, Samba KDC DB context, and auth session structures.

Risks: ownership contracts are mostly implicit: PAC pointers, `krb5_db_entry->e_data`, and context-owned cached user info must not be freed by callers incorrectly. API drift with MIT KDB flags can require header updates.

Test signals: compile all MIT plugin files, free/finalize context after operations, and validate each declared function is exercised by the KDB function table or policy path.
