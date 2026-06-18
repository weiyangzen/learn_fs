# sources/user-network-fs/samba/source3/winbindd/idmap_util.c

## Purpose
This file provides small utility helpers shared by idmap backends: range checking, locating maps in arrays, fetching idmap secrets, and allocating `struct id_map **` arrays with embedded SID storage.

## Important APIs, Types, And Functions
Exports are `idmap_unix_id_is_in_range`, `idmap_find_map_by_id`, `idmap_find_map_by_sid`, `idmap_fetch_secret`, and `id_map_ptrs_init`.

## Control Flow
Range checking treats zero low/high bounds as unbounded. Map lookup by ID scans to NULL termination. Map lookup by SID scans up to `IDMAP_LDAP_MAX_IDS` or NULL, whichever comes first. Secret fetching builds `IDMAP_<backend>_<domain>`, uppercases it, and calls `secrets_fetch_generic` with the supplied identity. `id_map_ptrs_init` allocates an array of pointers, a parallel array of maps, and a parallel array of zeroed SIDs, then wires each map to one SID and NULL-terminates the pointer list.

## State And Persistence
This file itself has no persistent state. `idmap_fetch_secret` reads Samba secrets storage.

## Dependencies And Integration
It depends on idmap types, SID equality, Samba secrets, and `IDMAP_LDAP_MAX_IDS`. LDAP and RFC2307 backends use the lookup helpers for batch result reconciliation.

## Risks And Test Signals
Test low/high zero semantics, boundary IDs, duplicate IDs/SIDs in arrays, arrays longer than `IDMAP_LDAP_MAX_IDS`, secret key case normalization, failed uppercase conversion, and allocation cleanup in `id_map_ptrs_init`. The SID lookup helper's fixed maximum is appropriate for LDAP batches but surprising for generic callers.
