## sources/user-network-fs/samba/source4/kdc/samba_kdc.h

Purpose: shared Samba KDC data structures used by DB glue, MIT/Heimdal adapters, and PAC logic.

Important types: `samba_kdc_policy` holds ticket lifetime policy. `samba_kdc_base_context` carries event/loadparm/messaging/SAMDB and current-time pointer used when creating DB contexts. `samba_kdc_db_context` stores DB runtime state, RODC identity, krbtgt metadata, policy, sequence context, and current-time pointer. `samba_kdc_entry` binds an SDB/DSDB record to a KDC entry, carrying LDB message, realm DN, cached PAC/DB user info, claims, authn policies, supported enctypes, reject status, trust/RODC/krbtgt flags, and enforced lifetime data. `CHANGEPW_LIFETIME` defines two-minute lifetime for changepw tickets.

Control flow and integration: these structs are the data backbone passed through `samba_kdc_fetch()`, SDB conversion, MIT `e_data`, Heimdal HDB context, and PAC generation.

State and persistence: structures cache DSDB-derived data for an entry lifetime but do not own durable storage except references to LDB messages and contexts. `current_nttime_ull` is used to align DSDB time-sensitive operations with KDC request time.

Dependencies: time, NTSTATUS, LDB, tevent/loadparm/messaging, DSDB, claims, authn policy, and Kerberos DB adapters.

Risks: lifetime comments matter: `sdb_entry.db_entry` is temporarily valid, while `kdc_entry` references Heimdal/MIT wrapper objects. Incorrect ownership causes use-after-free. Current-time pointer must be set before gMSA/authn policy operations.

Test signals: fetch/free KDC entries under MIT and Heimdal, RODC and trust entries, gMSA current time propagation, changepw ticket lifetime, and cache reuse of info/claims fields.
