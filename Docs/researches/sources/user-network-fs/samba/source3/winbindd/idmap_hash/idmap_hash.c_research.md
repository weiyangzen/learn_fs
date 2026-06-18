# sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.c

## Purpose
This deprecated backend maps SIDs to Unix IDs by hashing a domain SID and RID into a 31-bit ID. It also registers an NSS-info backend named `hash` that maps user aliases through an optional name-map file. It is only valid for the default `*` idmap configuration and is explicitly marked for migration away from the module.

## Important APIs, Types, And Functions
`struct sid_hash_table` holds a 4096-entry table of domain SID pointers keyed by a 12-bit hash. `hash_domain_sid`, `hash_rid`, `combine_hashes`, and `separate_hashes` implement the mapping math. `idmap_hash_initialize`, `unixids_to_sids`, and `sids_to_unixids` provide `struct idmap_methods`. `nss_hash_map_to_alias` and `nss_hash_map_from_alias` provide `struct nss_info_methods`. `idmap_hash_init` registers both the idmap and NSS-info interfaces.

## Control Flow
Initialization logs deprecation, rejects non-default domains, fetches the trusted-domain cache, skips null SIDs and domains with explicit idmap config, hashes valid domain SIDs, and stores them in the table. ID-to-SID splits the ID into domain hash and RID hash, looks up the domain SID table, composes a SID, and returns `ID_TYPE_BOTH`. SID-to-ID splits the RID from the SID, computes hashes, reuses or remembers the domain if it is known through the trusted-domain cache or `netsamlogon_cache_have`, and returns `ID_TYPE_BOTH`. If a domain is not yet known and the requested type is not specified, it sets `ID_REQUIRE_TYPE` to trigger parent fallback behavior.

## State And Persistence
State is memory-only in `dom->private_data`, with additional domain validity from the trusted-domain cache and samlogon cache. There is no durable allocation database; mappings are deterministic and collision-prone by construction. The NSS alias path reads the configured map file on each lookup through `mapfile.c`.

## Dependencies And Integration
The module integrates with idmap registration, NSS-info registration, winbind trusted-domain cache (`wcache_tdc_fetch_list`), domain configuration checks, SID helpers, samlogon cache, and mapfile lookup helpers. It relies on winbind parent behavior for fallback when a domain is unknown.

## Risks And Test Signals
Hash collisions can map unrelated domains/RIDs to the same Unix ID. Only SIDs with exactly four authorities are accepted by `hash_domain_sid`. RID zero maps to unmapped. Tests should cover default-domain enforcement, known-domain table population, samlogon-cache learning, collision behavior, `ID_REQUIRE_TYPE`, and partial mapping return codes. Also test build coverage with `mapfile.c`: `mapfile_lookup_value` appears to check `!*key` after assigning `*value`, which is not a valid local variable in that function and should be caught by compilation.
