# sources/user-network-fs/samba/source4/dns_server/dns_utils.c

## Purpose
`dns_utils.c` is a thin adapter between the DNS server runtime and the shared `dnsserver_common` AD database helpers. It gives server modules concise functions for exact/wildcard record lookup, record replacement, authority checks, authoritative zone selection, and DNS-name-to-LDB-DN conversion.

## Important APIs, Types, and Functions
- `dns_lookup_records()` calls `dns_common_lookup()` for exact, non-wildcard lookup.
- `dns_lookup_records_wildcard()` calls `dns_common_wildcard_lookup()` to allow wildcard fallback.
- `dns_replace_records()` calls `dns_common_replace()` with a hard-coded serial value.
- `dns_authoritative_for_zone()` checks whether a DNS name falls under any loaded zone and treats the empty name as authoritative.
- `dns_get_authoritative_zone()` returns the first loaded matching zone name.
- `dns_name2dn()` delegates to `dns_common_name2dn()` using `dns->samdb` and `dns->zones`.

## Control Flow
All functions are direct wrappers except the two zone authority helpers. Authority matching iterates the loaded `dns->zones` list and uses `dns_name_match()` to compare suffixes case-insensitively while computing host-part length. `dns_get_authoritative_zone()` returns on the first match; zone sorting in `dns_common_zones()` makes this prefer longer/specific zones.

## State and Persistence
This file owns no durable state. It reads `dns->zones` and `dns->samdb`, and replacement persists by forwarding to `dns_common_replace()`. The static `dwSerial = 110` in `dns_replace_records()` is written into records by common replacement code.

## Dependencies and Integration Points
Dependencies are `samdb`, `dns_server.h`, and `dnsserver_common` helpers. Query and update modules use these wrappers so they do not need to know the lower-level common helper signatures.

## Risks and Edge Cases
- The hard-coded serial `110` is marked TODO and may not represent real SOA serial behavior.
- Authority checks rely on the in-memory zone list being current; IRPC reload is required after zone changes.
- The empty root name is treated as authoritative independent of loaded zones.

## Test Signals
Useful tests include exact vs wildcard lookup behavior, authoritative matching with overlapping zones, empty-name/root behavior, stale-zone-list behavior before/after reload, and verification that replacements carry the expected serial/tombstone semantics from `dns_common_replace()`.
