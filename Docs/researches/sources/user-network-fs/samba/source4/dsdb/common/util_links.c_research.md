# sources/user-network-fs/samba/source4/dsdb/common/util_links.c

## Purpose
This file provides helpers for comparing and locating linked-attribute DNs stored in DSDB. It supports replication-compatible ordering by NDR GUID byte order, lazy parsing of trusted DN values, and binary-search lookup of existing links by GUID plus optional link metadata/extra-part comparison.

## Important APIs, Types, and Functions
`ndr_guid_compare()` serializes two `struct GUID` values into fixed NDR blobs and compares the raw blob bytes, matching DRS replication ordering rather than `GUID_compare()` ordering. `really_parse_trusted_dn()` converts a stored `struct ldb_val` into a trusted `struct dsdb_dn`, extracts its `GUID` extended component, and fills a `struct parsed_dn`. `get_parsed_dns_trusted()` allocates an array of `struct parsed_dn` entries and stores value pointers without parsing immediately. `parsed_dn_find()` searches a sorted parsed-DN array for a target GUID and returns exact and next insertion-point pointers. The static comparator `la_guid_compare_with_trusted_dn()` lazily parses database-side DNs and optionally compares `dsdb_dn->extra_part` exactly or by prefix.

## Control Flow, State, and Persistence
The common path builds a `compare_ctx` containing the target GUID, LDB context, LDAP syntax OID, optional extra part, partial-prefix length, and error field. `BINARY_ARRAY_SEARCH_GTE()` calls the comparator, which parses entries on demand and sets `ctx.err` if parsing fails. If a target GUID is all zero, `parsed_dn_find()` cannot use the sorted GUID key; it logs the replication edge case, requires a target DN, linearly parses and compares by DN, and if no match is found returns the beginning of the list as the insertion point. The helpers do not write persistent state; they mutate only the caller-owned parsed array by caching parsed `dsdb_dn` and `guid` fields.

## Dependencies and Integration
The code depends on DSDB DN parsing (`dsdb_dn_parse_trusted()`), extended-DN GUID extraction, NDR GUID serialization, Samba binary-search helpers, data-blob comparison, and LDB DN comparison. It is used by linked-attribute and replication metadata paths that must preserve Windows/DRS sort order for link values and identify links efficiently during add/delete/update processing.

## Risks
Correctness depends on the input array already being sorted with the same NDR GUID ordering. Parse errors are reported through a compare-function side channel where zero can mean either equality or error, so callers must check the final returned LDB code. Prefix matching of `extra_part` is intentional but easy to misuse if the caller expects full metadata equality. NULL GUID fallback is best-effort and can place an unknown deleted link at the start of the list, so replication edge cases should be logged and tested.

## Test Signals
Tests should compare `ndr_guid_compare()` against known NDR byte-order examples, lazy parsing success and failure, binary search exact hit/miss/insertion point, extra-part exact comparison, partial extra-part prefix comparison, all-zero GUID with matching and missing target DN, all-zero GUID without target DN returning an operations error, and behavior when a stored trusted DN lacks a GUID component.
