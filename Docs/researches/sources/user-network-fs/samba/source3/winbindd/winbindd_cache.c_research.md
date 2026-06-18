# sources/user-network-fs/samba/source3/winbindd/winbindd_cache.c

## Purpose

`winbindd_cache.c` implements winbindd's persistent cache database for domain lookups, policy queries, offline logon credentials, trusted-domain metadata, and selected NDR-level winbind responses. It backs the `wb_cache_*` API used by domain backends and preserves enough state in `winbindd_cache.tdb` for cached logons and lookup fallback when a DC is unavailable.

## Important APIs, Types, and Functions

- `struct winbind_cache` wraps the global `TDB_CONTEXT *tdb`; `struct cache_entry` is the serialized centry format with status, sequence number, timeout, and packed payload.
- Cache policy and lifecycle: `winbindd_use_cache()`, `winbindd_set_use_cache()`, `winbindd_flush_caches()`, `get_cache()`, `wcache_open()`, `wcache_flush_cache()`, `close_winbindd_cache()`.
- Serialization helpers: `centry_*` readers/writers for integers, strings, hashes, SIDs, `NTTIME`, `time_t`, and `NTSTATUS`.
- Generic centry flow: `wcache_fetch()`, `centry_start()`, `centry_end()`, `centry_expired()`, `refresh_sequence_number()`.
- Main lookup wrappers: `wb_cache_name_to_sid()`, `wb_cache_sid_to_name()`, `wb_cache_rids_to_names()`, `wb_cache_query_user_list()`, `wb_cache_enum_dom_groups()`, `wb_cache_enum_local_groups()`, `wb_cache_lookup_usergroups()`, `wb_cache_lookup_useraliases()`, `wb_cache_lookup_aliasmem()`, `wb_cache_lookup_groupmem()`, `wb_cache_lockout_policy()`, `wb_cache_password_policy()`.
- Credential and offline APIs: `wcache_get_creds()`, `wcache_save_creds()`, `wcache_count_cached_creds()`, `wcache_remove_oldest_cached_creds()`, `set_global_winbindd_state_offline()`, `set_global_winbindd_state_online()`, `get_global_winbindd_state_offline()`.
- Maintenance APIs: `winbindd_validate_cache()`, `winbindd_validate_cache_nobackup()`, `winbindd_cache_validate_and_initialize()`, trusted-domain-cache helpers, and `wcache_fetch_ndr()`/`wcache_store_ndr()`.

## Control Flow

Cached calls initialize the domain backend and cache through `get_cache()`, try a cache-specific fetch path, refresh/check the domain sequence number, and accept the entry only if `centry_expired()` allows it. Misses call `domain->backend`, may mark the domain offline on timeout/DC-not-found, and store successful responses with centry writers.

Name/SID mapping uses `namemap_cache` rather than generic centries. User, group, alias, list, and policy queries use centry keys like `UL/`, `GL/`, `UG/`, `UA`, `AM/`, `GM/`, `LOC_POL/`, and `PWD_POL/`, decoding in the same order as encoding. Validation traverses TDB keys, dispatches by prefix, and upgrades v1 records to v2 by inserting timeout fields.

## State and Persistence Behavior

The persistent database is `state_path(..., "winbindd_cache.tdb")`. If offline logon is disabled it may be cleared on first opener; if offline logon is enabled it persists across restart and is validated/backed up. Generic centries store status, sequence, timeout, and payload. Non-centry keys include `SEQNUM/`, `TRUSTDOMCACHE/`, `WINBINDD_OFFLINE`, `NDR/`, and the cache version key.

Offline behavior is intentional: global offline logon and per-domain offline states keep cached entries usable beyond normal expiry. Credential records store salted verifier material for offline logon. Trusted-domain and selected NDR responses are also persisted in the same TDB.

## Dependencies and Integration Points

The file bridges winbind callers to passdb, built-in, RPC, and ADS backends. It integrates with TDB, validation helpers, `namemap_cache`, `samlogon_cache`, NSS alias mapping, GnuTLS hashing, passdb machine SID helpers, ADS code, and connection-management functions such as `init_dc_connection()` and `set_domain_offline()`.

## Risks and Edge Cases

String payloads are limited to 254 bytes. Malformed centry payloads can panic outside validation mode. Offline mode deliberately returns stale data. NDR cache validation does not parse/checksum responses. `wcache_remove_oldest_cached_creds()` deserves scrutiny because eviction depends on interpreting cached credential timestamps correctly across historical formats.

## Test Signals

Test centry round trips for all key prefixes, online/offline/global-offline expiry behavior, validation failures, v1-to-v2 upgrade, salted and legacy credential reads, credential eviction, trusted-domain pack/unpack, NDR sequence/timeout invalidation, and backend timeout fallback to cached data.
