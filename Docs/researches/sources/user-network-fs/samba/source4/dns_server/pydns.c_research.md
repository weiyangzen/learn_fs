# sources/user-network-fs/samba/source4/dns_server/pydns.c

## Purpose
`pydns.c` implements the `samba.dsdb_dns` Python extension. It exposes selected AD DNS database helpers to Python so tooling can look up, extract, replace, compare, and timestamp DNS records using the same C implementation as the server.

## Important APIs, Types, and Functions
- `py_dnsp_DnssrvRpcRecord_get_list()` converts C `dnsp_DnssrvRpcRecord` arrays to Python `samba.dcerpc.dnsp.DnssrvRpcRecord` objects.
- `py_dnsp_DnssrvRpcRecord_get_array()` validates and copies a Python list of DNSP records into a C array.
- Python methods: `lookup`, `extract`, `replace`, `replace_by_dn`, `records_match`, `unix_to_dns_timestamp`, and `dns_timestamp_to_nt_time`.
- `MODULE_INIT_FUNC(dsdb_dns)` creates the extension module.

## Control Flow
`lookup(ldb, dns_name, dns_partition=None)` validates the Python LDB object, optionally accepts a DNS partition DN, enumerates zones, maps the DNS name to a DN, exact-lookups records, and returns `(dn, records)`. `extract(ldb, message_element)` decodes a raw `dnsRecord` LDB message element. `replace(ldb, dns_name, records)` maps name to DN and calls common replacement. `replace_by_dn(ldb, dn, records)` skips name mapping and replaces by supplied DN. `records_match()` delegates to C update matching semantics. Timestamp helpers validate Python integer ranges and call common conversion routines.

## State and Persistence
The module does not own persistent state, but `replace` and `replace_by_dn` mutate AD DNS records through `dns_common_replace()`. Both use the same hard-coded serial `110` as the internal DNS utility wrapper and pass `needs_add=false`, so they replace existing nodes rather than creating absent ones.

## Dependencies and Integration Points
It depends on Python C API compatibility headers, pyldb, pytalloc, Samba Python module registration, generated DNSP NDR Python bindings, LDB/SAMDB, and `dnsserver_common`. The build file installs it as `samba/dsdb_dns.so`.

## Risks and Edge Cases
- `PyList_SetItem()` steals references; the code assumes `py_return_ndr_struct()` succeeds for each item and does not explicitly handle NULL per item.
- `py_dnsp_DnssrvRpcRecord_get_array()` returns early on type/reference failure without freeing intermediate references until the stack frame is freed by callers.
- `replace()` cannot add a missing DNS node because `needs_add=false`.
- Timestamp conversion rejects values outside C `time_t` or uint32/NTTIME range, which is correct but visible to Python callers.

## Test Signals
Useful tests include Python lookup with and without DNS partition, extract from raw `dnsRecord`, replace existing records, replace missing-name failure, record matching parity with server update semantics, invalid Python object types, and timestamp conversion boundary values.
