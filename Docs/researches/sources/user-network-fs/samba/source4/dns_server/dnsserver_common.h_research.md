# sources/user-network-fs/samba/source4/dns_server/dnsserver_common.h

## Purpose
`dnsserver_common.h` declares the shared DNS database helper interface used across Samba DNS components. It defines the zone list type, WERROR-to-DNS helpers, record lookup/extract/replace contracts, name validation/matching, zone enumeration, zone property loading, operation logging, and DNS timestamp conversion.

## Important APIs, Types, and Functions
- `DNS_ERR()` creates DNS RCODE-flavored WERROR constants; `werr_to_dns_err()` converts them to wire rcodes.
- `struct dns_server_zone` links zone name and LDB DN in a doubly linked list.
- Lookup/extract APIs: `dns_common_extract()`, `dns_common_lookup()`, `dns_common_wildcard_lookup()`.
- Mutation API: `dns_common_replace()`.
- Validation/mapping APIs: `dns_name_check()`, `dns_name_match()`, `dns_common_name2dn()`, `samba_dns_name_equal()`.
- Metadata APIs: `dns_get_zone_properties()`, `dns_zoneinfo_load_zone_property()`, `dns_common_zones()`.
- Record/time APIs: `dns_name_is_static()`, `dns_record_match()`, `unix_to_dns_timestamp()`, `dns_timestamp_to_nt_time()`.
- `DNS_COMMON_LOG_OPERATION` emits duration/result/zone/name/data debug logs.

## Control Flow
The header sets a layered contract: callers enumerate zones, map DNS names to DNs, look up or replace `dnsRecord` values, and translate internal errors to DNS protocol rcodes. It also makes logging consistent for common operations by wrapping debug-level timing output in a macro.

## State and Persistence
No state is stored in the header. It describes AD-backed persistence through `ldb_context`, `ldb_dn`, `dns_server_zone`, `dnsp_DnssrvRpcRecord`, and `dnsserver_zoneinfo` parameters. `NTTIME_TO_HOURS` defines the timestamp conversion unit used for persisted DNS aging timestamps.

## Dependencies and Integration Points
The header includes RPC DNS server declarations and forward-declares LDB/DNSP structures. It is consumed by internal DNS service code, DLZ code, Python bindings, and likely DNS RPC management paths.

## Risks and Edge Cases
- The macro `DNS_COMMON_LOG_OPERATION` evaluates supplied expressions into local variables; callers should avoid side-effect expressions.
- Callers must understand whether `dns_common_lookup()` should include tombstoned nodes via a non-NULL `tombstoned` pointer.
- The shared API exposes low-level replacement semantics, so misuse can tombstone or resurrect nodes.

## Test Signals
Header contracts are exercised by compilation and by tests around common implementation. ABI/API-sensitive tests should include callers from internal DNS, DLZ, and Python modules to catch signature or semantic drift.
