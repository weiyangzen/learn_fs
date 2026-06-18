# sources/user-network-fs/samba/source3/libsmb/namecache.c

## Purpose
This file implements the NetBIOS name cache on top of Samba `gencache`. It stores and retrieves NetBIOS name-to-address lists and node-status-derived name records so name resolution can avoid repeated WINS, broadcast, LMHOSTS, or node status traffic.

## Important APIs, Types, And Functions
Public functions are `namecache_store`, `namecache_fetch`, `namecache_delete`, `namecache_flush`, `namecache_status_store`, and `namecache_status_fetch`. Internal helpers include `ipstr_list_make_sa`, `ipstr_list_parse`, `namecache_key`, `flush_netbios_name`, and `namecache_status_record_key`. Address data is represented as `struct samba_sockaddr` arrays and persisted as comma-separated numeric address strings.

## Control Flow
`namecache_store` rejects artificial name types above 255, builds an uppercase `NBT/<name>#<type>` key, serializes the address list as `addr:0` or `[ipv6]:0`, and writes it to `gencache` with `lp_name_cache_timeout()` expiry. `namecache_fetch` builds the same key, retrieves the stored string, tokenizes on commas, strips optional ports, handles bracketed IPv6, converts numeric strings into `sockaddr_storage`, and returns a talloc-owned `struct samba_sockaddr` array only when at least one address parses.

`namecache_delete` removes a single name/type key. `namecache_flush` iterates `NBT/*` entries and deletes each. Status records use keys shaped like `NBT/<query>#<query_type>.<wanted_type>.<ip>` and store the server name found by a node status response.

## State And Persistence
All durable state lives in `gencache` and expires using `lp_name_cache_timeout()`. The module serializes only numeric addresses and ignores stored ports on read. Status fetch copies returned server names into a 16-byte NetBIOS-name-sized output buffer with `strlcpy`.

## Dependencies And Integration Points
The file depends on `lib/gencache.h`, Samba socket helpers (`print_sockaddr`, `interpret_string_addr`, `sockaddr_storage_to_samba_sockaddr`), talloc tokenization, and `libsmb/namequery.h` declarations. It is consumed by `namequery.c` for normal name resolution and node status lookups, and by `namequery_dc.c` to invalidate DC-related cache entries when ADS site selection changes.

## Risks And Edge Cases
The comma-separated format assumes addresses are numeric and never contain unbracketed commas. The writer stores port `0`, and the parser deliberately ignores ports, so callers must not expect service-port fidelity. Corrupt cache entries can parse to zero addresses and are treated as misses. `namecache_flush` deletes every `NBT/*` entry, including status records, not just address-list records. The string append loop in `ipstr_list_make_sa` is intentionally inefficient but acceptable for small address lists.

## Test Signals
Tests should cover IPv4 and bracketed IPv6 round trips, invalid token tolerance, name types above 255, cache expiry behavior through `gencache`, flushing `NBT/*`, status record keying by source IP and type, and fetch behavior when all serialized addresses are invalid.
