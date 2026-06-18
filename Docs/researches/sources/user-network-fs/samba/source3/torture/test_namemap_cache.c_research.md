# sources/user-network-fs/samba/source3/torture/test_namemap_cache.c

Purpose: This file tests the name/SID mapping cache, including invalid cache payload rejection, case-insensitive domain/name lookup, empty-domain handling, and domain-only entries with an empty account name.

Important APIs/types/functions: Callback helpers `namemap_cache1_fn1()` through `namemap_cache1_fn6()` validate returned domain/name/type or SID/type values. `run_local_namemap_cache1()` uses `gencache_set()`, `namemap_cache_set_sid2name()`, `namemap_cache_find_sid()`, `namemap_cache_set_name2sid()`, and `namemap_cache_find_name()`. It uses well-known SIDs `global_sid_Network`, `global_sid_World`, and a local domain SID constant.

Control flow: The test first stores an invalid raw gencache value for `SID2NAME/S-1-5-2` and expects the namemap parser not to accept it. It then stores and finds `NT Authority\Network` both by SID and by lower-case name, verifies a missing name lookup fails, repeats the process for an empty-domain `Everyone` mapping, and finally tests a domain-only mapping `SAMBA-DOM` with empty name.

State/persistence behavior: State is stored in Samba's generic cache with explicit expirations of `time(NULL)+60`. The test mutates shared cache keys for well-known SIDs. Returned `expired` flags are supplied to callbacks but the callbacks focus on values and SID types.

Dependencies and integration points: It depends on `lib/namemap_cache.h`, SID helpers, gencache, and LSA SID type enums. It covers cache behavior used by name resolution and SID lookup paths.

Risks: Cache pollution from earlier runs can matter for the same well-known keys, although the test overwrites the keys it uses. Time-based expiry is short but should not expire during normal execution. Case normalization behavior is part of the contract and must be preserved.

Test signals: Passing requires invalid gencache data to be rejected, all stored mappings to be found with expected normalized domain/name/type or SID/type, missing `foo\bar` to fail, and empty-domain/domain-only cases to round-trip.
