# sources/user-network-fs/samba/source4/kdc/hdb-samba4.c

## Purpose
`hdb-samba4.c` adapts Samba's SDB/database glue to Heimdal's HDB interface. It makes the Samba AD database appear as a read-mostly Kerberos principal database, wires HDB fetch/iteration/delegation/audit hooks, and carries Samba authentication/audit details through Heimdal request objects.

## Important APIs, Types, And Functions
The main exported constructors are `hdb_samba4_create_kdc` and `hdb_samba4_kpasswd_create_kdc`. Exported request helpers are `hdb_samba4_set_ntstatus`, `hdb_samba4_set_steal_client_audit_info`, and `hdb_samba4_set_steal_server_audit_info`. Important static hooks include `hdb_samba4_fetch_kvno`, `hdb_samba4_kpasswd_fetch_kvno`, first/next iteration, `hdb_samba4_check_constrained_delegation`, `hdb_samba4_check_rbcd`, PKINIT/client-target checks, and `hdb_samba4_audit`.

## Control Flow
HDB fetch converts HDB flags to SDB flags, delegates to `samba_kdc_fetch`, maps SDB errors to HDB errors, then converts `sdb_entry` to `hdb_entry`. The kpasswd variant always looks up `kadmin/changepw@REALM`, clears client/krbtgt lookup flags, and requests the latest kvno. Iteration delegates to `samba_kdc_firstkey`/`nextkey`; the kpasswd HDB panics on iteration because it should only be used as a keytab. Constructor setup fills the `HDB` vtable, disables unsupported mutable operations, and enables enterprise principal handling. Audit flow reads Heimdal request KV pairs, maps auth events to NTSTATUS/Kerberos errors, may attach NTSTATUS e-data, updates bad password/lockout accounting, and logs authentication or authorization events.

## State And Persistence Behavior
The HDB object owns a `samba_kdc_db_context` from `samba_kdc_setup_db_ctx`. It does not store entries through HDB; store/rename/delete return database-in-use or are null. Persistence changes occur indirectly through DB glue accounting and bad-password updates. Audit information and NTSTATUS metadata are stored as Heimdal request objects with custom deallocators, stealing talloc-owned audit data where needed.

## Dependencies And Integration Points
This file integrates Heimdal HDB, Samba SDB conversion, PAC/delegation glue, authentication accounting, authn policy, winbind IRPC for bad-password reset propagation on RODCs, tsocket address conversion, and Samba audit logging. `kdc-heimdal.c` installs the HDB into the live KDC; `hdb-samba4-plugin.c` exposes it as an HDB method for keytab use.

## Risks
Risk concentrates in error mapping and audit side effects. Returning `HDB_ERR_NOT_FOUND_HERE` controls RODC forwarding, so incorrect mapping changes availability/security. Bad-password and lockout handling must not double-count or fail open. Request-owned Heimdal objects wrap talloc pointers, so ownership bugs could leak or double free audit info. `hdb_samba4_audit` intentionally panics under socket-wrapper tests for unexpected generic internal situations, making tests a useful tripwire.

## Test Signals
Test HDB fetch for clients, services, krbtgt, trusts, wrong realm, missing RODC secrets, and kpasswd. Exercise AS audit outcomes: unknown client, preauth required suppression, wrong long-term key, historic key, lockout, PKINIT mismatch/failure, RODC fallback, and NTSTATUS e-data. Test TGS audit and delegation/RBCD hooks.
