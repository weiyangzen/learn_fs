# sources/user-network-fs/samba/source4/kdc/db-glue.h

## Purpose
`db-glue.h` declares the public interface for Samba's KDC database glue. It lets KDC/HDB code fetch principals, iterate entries, convert DSDB messages into key material, validate special Kerberos relationships, and initialize per-KDC database context.

## Important APIs, Types, And Functions
The header forward-declares `struct sdb_keys`, `struct sdb_entry`, `struct samba_kdc_base_context`, `struct samba_kdc_db_context`, and `struct samba_kdc_entry`. `enum samba_kdc_ent_type` distinguishes client, server, krbtgt, trust, and any-entry conversions. Public functions include `samba_kdc_message2entry_keys`, `samba_kdc_set_fixed_keys`, `samba_kdc_fetch`, sequential iteration via `samba_kdc_firstkey`/`samba_kdc_nextkey`, delegation and PKINIT checks, `samba_kdc_setup_db_ctx`, and `dsdb_extract_aes_256_key`.

## Control Flow
Consumers typically call `samba_kdc_setup_db_ctx` once, then use `samba_kdc_fetch` for single-principal lookups or first/next iteration for keytab/admin export. `samba_kdc_message2entry_keys` is exposed separately so DSDB code can parse Kerberos keys without duplicating the complicated credential parsing in `db-glue.c`.

## State And Persistence Behavior
The declarations expose DB context construction but not the fields. State lives in the opaque `samba_kdc_db_context`, which owns SAMDB access, policy, current-time pointers, iteration state, and krbtgt identity. The header itself has no persistence behavior.

## Dependencies And Integration Points
The API crosses Samba DSDB, Heimdal/MIT SDB/HDB, Kerberos principal/key handling, and KDC plugin code. It is included by the HDB adapter, KDC glue header, and any DSDB module that needs AES key extraction.

## Risks
Because this header publishes low-level security operations, flag semantics must remain stable. Callers must pass the correct entity type and SDB flags; wrong flags can expose history keys, suppress policy checks, or return a client when a server was required.

## Test Signals
Build tests should catch prototype drift. Runtime tests should exercise each exported path through HDB fetch, keytab export, PKINIT UPN match, constrained delegation, S4U2Proxy, and AES extraction.
