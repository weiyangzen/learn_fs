# sources/user-network-fs/samba/source3/winbindd/winbindd_creds.c

## Purpose

`winbindd_creds.c` wraps offline cached logon credential storage and retrieval. It ties the persistent winbind credential cache to the Netlogon `SamInfo3` cache so cached authentication can retrieve both verifier material and logon metadata.

## Important APIs, Types, and Functions

- `MAX_CACHED_LOGINS` limits persistent cached credential records to 10.
- `winbindd_get_creds()` reads `CRED/<sid>` material through `wcache_get_creds()` and fetches matching `SamInfo3` from `netsamlogon_cache_get()`.
- `winbindd_store_creds()` stores password verifier material and optional SamInfo3.
- `winbindd_update_creds_by_info3()` and `winbindd_update_creds_by_name()` call `winbindd_store_creds()`.

## Control Flow

Retrieval first fetches cached password material by SID, then requires a matching SamInfo3 record. Storage derives the credential SID from supplied `info3` or resolves the username through `lookup_cached_name()`. With a password, it counts cached credentials, evicts when the limit would be exceeded, hashes the password with `E_md4hash()`, and stores salted verifier material with `wcache_save_creds()`. With both `info3` and username, it stores SamInfo3 and marks `NETLOGON_CACHED_ACCOUNT`.

## State and Persistence Behavior

Persistent verifier records live in `winbindd_cache.tdb`; SamInfo3 records live in the samlogon cache. This file holds no process-local state. Passwordless updates may store only SamInfo3.

## Dependencies and Integration Points

It depends on `wcache_*` credential APIs, `lookup_cached_name()`, Netlogon SamInfo3 structures, `netsamlogon_cache_get()`/`store()`, SID helpers, and Samba password hashing. It is used by online auth update paths and offline auth retrieval paths.

## Risks and Edge Cases

Cached login needs both verifier and SamInfo3. Username-only storage fails if no cached name-to-SID mapping exists. Eviction depends on lower-level oldest-record logic. The supplied `info3` is modified in place by setting `NETLOGON_CACHED_ACCOUNT`.

## Test Signals

Test storing with SamInfo3, storing by username, missing mapping failures, limit eviction, same-SID replacement, retrieval requiring both records, salted credential output, and samlogon store failure.
