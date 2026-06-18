# sources/user-network-fs/samba/source4/dns_server/dnsserver_common.c

## Purpose
`dnsserver_common.c` is the shared AD DNS database implementation used by the internal DNS server, BIND DLZ modules, and Python tooling. It maps WERRORs to DNS rcodes, decodes and encodes `dnsRecord` NDR blobs, looks up exact and wildcard DNS nodes, validates DNS names and target names, manages tombstone/aging behavior, maps DNS names to AD DNs, enumerates zones, compares records, and converts DNS timestamps.

## Important APIs, Types, and Functions
- `werr_to_dns_err()` maps Samba/WERROR status to DNS wire rcodes.
- `dns_common_extract()` decodes `dnsRecord` values into `dnsp_DnssrvRpcRecord` arrays and overwrites SOA MNAME with the local DNS hostname on writable DCs.
- `dns_common_lookup()` performs exact base-object lookup and can include tombstoned nodes for update handling.
- `dns_common_wildcard_lookup()` performs exact lookup first and then wildcard fallback using `build_wildcard_query()` and `get_best_match()`.
- `dns_name_check()` enforces DNS label/name limits.
- `dns_get_zone_properties()` and `dns_zoneinfo_load_zone_property()` decode `dNSProperty` values into RPC zone info, especially aging/scavenging data.
- `dns_common_replace()` encodes replacement records, applies aging refresh, handles tombstone transitions, and calls `ldb_add()` or `ldb_modify()`.
- `dns_common_name2dn()` maps DNS names to `DC=<host>,DC=<zone>,...` nodes, with `DC=@` for zone apex.
- `dns_record_match()`, `dns_name_match()`, `samba_dns_name_equal()`, `dns_common_zones()`, `unix_to_dns_timestamp()`, and `dns_timestamp_to_nt_time()` provide shared matching, zone enumeration, and time conversion.

## Control Flow
Lookup begins with an LDB search for `objectClass=dnsNode`, optionally excluding `dNSTombstoned=TRUE`. Missing objects become `WERR_DNS_ERROR_NAME_DOES_NOT_EXIST`; malformed or failed searches become DNS name/server errors. Extract decodes each NDR record and adjusts SOA MNAME on writable DCs.

Wildcard lookup validates the RDN, skips wildcarding for `@`, performs an exact lookup, and only on missing records builds an LDB parse tree matching the exact name plus progressively shorter `*.<suffix>` candidates. The longest candidate wins unless an exact match is present.

Replacement builds an LDB message with `dnsRecord` replace semantics, loads zone properties for aging, validates target names inside records, sorts records by type descending then timestamp ascending, filters deletion tombstone placeholders, refreshes timestamps when aging/no-refresh rules allow, stamps serial, NDR-encodes records, adds a new `dnsNode` when requested, or modifies an existing node. If no live records remain, it writes a real tombstone record and `dNSTombstoned=TRUE`; if resurrecting, it flips tombstoned false.

Name-to-DN conversion handles the empty root server name specially, validates names, finds the authoritative zone, maps the apex to `DC=@`, maps non-apex host parts to a single `DC` RDN, validates/casefolds the DN, and returns it.

## State and Persistence
Persistent state is AD DS data: `dnsZone` objects, `dnsNode` objects, `dnsRecord` NDR values, `dNSTombstoned`, and `dNSProperty`. The module also uses rootDSE/local `dnsHostName`, RODC status, and zone aging properties to shape returned or stored records. Timing logs are emitted when DNS debug is high.

## Dependencies and Integration Points
The code depends on LDB/DSDB search and modify helpers, generated DNS/DNSP NDR codecs, RPC DNS server structures, network address parsing for AAAA comparison, dlink-list zone structures, and Samba time utilities. It is intentionally shared by internal DNS, DLZ, and Python bindings.

## Risks and Edge Cases
- Wildcard query construction assumes the RDN name is validated and NUL-terminated; callers must not bypass validation.
- `dns_name_check()` is called with `strlen()` in many paths and therefore cannot validate embedded NUL unless the caller uses length-aware input first.
- Tombstone handling has nuanced placeholder vs persisted tombstone semantics; wrong `EntombedTime` values can change deletion behavior.
- Zone sorting only sorts by length and has a TODO for partition priority, so equal-length duplicate zone names across partitions depend on search order.
- Aging refresh uses unsigned arithmetic on DNS timestamps; unusual/future timestamps may behave unexpectedly.

## Test Signals
Coverage should include NDR extract failures, SOA MNAME rewrite on writable DC vs RODC, exact and wildcard lookup ordering, invalid DNS names, target-name validation in CNAME/MX/NS/PTR/SRV/SOA, adding nodes, replacing existing records, tombstoning and resurrection, zone property decoding, zone enumeration exclusions for `RootDNSServers` and `..TrustAnchors`, record matching for IPv6 canonical forms, and timestamp overflow conversion.
