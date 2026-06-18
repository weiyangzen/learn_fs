# sources/user-network-fs/samba/source4/dsdb/common/util_trusts.c

## Purpose

`util_trusts.c` is the DSDB trust utility implementation for Active Directory trusted domain objects, forest trust information, trust routing, and claims transformation policy lookup. It converts local `crossRef` partition objects and trustedDomain (`TDO`) records into LSA trust structures, builds forest-trust record lists, normalizes and merges forest trust data, detects collisions, searches trustedDomain objects by name/SID/type, extracts incoming trust passwords, and builds a routing table used by name/SID trust resolution.

## Important APIs, Types, and Functions

- `dsdb_trust_forest_info_add_record()` is the internal copy/validation helper for `lsa_ForestTrustRecord2` entries. It deep-copies DNS, NetBIOS, SID, scanner-info, and binary records into a `lsa_ForestTrustInformation2` array and rejects malformed names, missing mandatory strings, overlong NetBIOS names, and invalid record types.
- `dsdb_trust_parse_crossref_info()`, `dsdb_trust_crossref_tdo_info()`, `dsdb_trust_local_tdo_info()`, and `dsdb_trust_xref_tdo_info()` synthesize `lsa_TrustDomainInfoInfoEx` structures from `crossRef` records under `CN=Partitions`.
- `dsdb_trust_xref_forest_info()` enumerates local forest crossRefs and UPN/SPN suffixes into an LSA forest-trust information list.
- `dsdb_trust_parse_tdo_info()`, `dsdb_trust_parse_forest_info()`, and `dsdb_trust_default_forest_info()` parse TDO attributes and create default forest trust blobs.
- `dsdb_trust_normalize_forest_info_step1()` validates, copies, de-duplicates, strips one trailing dot from DNS names, and checks TLN/domain relationships while preserving original indexes by leaving duplicate slots as NULL.
- `dsdb_trust_normalize_forest_info_step2()` compacts/reorders records in Windows-compatible order and assigns timestamps where missing.
- `dsdb_trust_verify_forest_info()` compares new forest-trust information against a reference forest and records TLN, NetBIOS, and SID collisions in `lsa_ForestTrustCollisionInfo`.
- `dsdb_trust_merge_forest_info()` merges existing and newly discovered forest trust information, preserving admin-disabled domain records, exclusions, scanner info, binary records, times, and flags where applicable.
- `dsdb_trust_search_tdo()`, `dsdb_trust_search_tdo_by_type()`, `dsdb_trust_search_tdo_by_sid()`, and `dsdb_trust_search_tdos()` are search helpers over the local System container.
- `dsdb_trust_get_incoming_passwords()` parses `trustAuthIncoming`, selects current/previous NTOWF trust passwords, and hashes cleartext secrets with MD4.
- `dsdb_trust_routing_table_load()`, `dsdb_trust_routing_by_name()`, `dsdb_trust_domain_by_sid()`, and `dsdb_trust_domain_by_name()` build and query in-memory routing state for trusted forests/domains.
- `dsdb_trust_get_claims_tf_policy()` validates a TDO-linked claims transformation policy DN, reads `msDS-TransformationRules`, unwraps XML, and parses the claims rule set.

## Control Flow

The crossRef path starts at a domain DN, searches `CN=Partitions` for the matching `crossRef`, parses its DNS/NetBIOS/SID from `ncName` extended DN metadata, and optionally follows `rootTrust` and `trustParent` crossRef links. Forest info generation then sorts crossRefs so forest-root and parent domains are handled predictably, adds top-level names and domain-info records, adds UPN/SPN suffixes that are not covered by existing TLNs, and removes child TLNs when a parent TLN covers the same namespace.

Forest trust normalization is split into two explicit phases. Step 1 deep-copies input, sanitizes DNS names, rejects impossible TLN/exclusion/domain relationships, and NULLs duplicates while retaining count/index positions for collision reporting. Step 2 traverses the Step 1 result in reverse groups: TLN/TLN_EX first, domain-info second, scanner-info third, binary data last. It also fills zero timestamps with the current time.

Collision verification scans each new TLN and domain-info record against a reference forest trust list. For TLNs, overlapping enabled names produce `LSA_TLN_DISABLED_CONFLICT` unless exclusions or disabled flags allow coexistence. For domain-info records, SID and NetBIOS conflicts set corresponding disabled flags, while DNS and NetBIOS strings may be normalized to existing casing. Merge then constructs a final list by adding unique TLNs, unique domains, retained admin-disabled old domains, still-valid exclusions, scanner records, and binary records.

Routing-table loading first models the local domain from crossRef data. If the local domain is the forest root, or the local domain has a root-direction TDO, it attaches local forest info generated from crossRefs. It then appends all TDOs, parsing forest trust blobs for forest-transitive trusts. Routing lookups iterate this list and prefer exact NetBIOS/DNS/SID matches or the most specific enabled TLN that covers a child name.

## State and Persistence Behavior

Most functions build talloc-owned transient structures, but their inputs and outputs mirror persisted AD data. Persistent reads include `crossRef` attributes, `trustedDomain` attributes, `msDS-TrustForestTrustInfo`, `trustAuthIncoming`, `uPNSuffixes`, `msDS-SPNSuffixes`, and claims policy objects. This file itself does not usually modify LDB state; it prepares data for callers that write trust blobs or make routing decisions. Password extraction zeroes the local selected password structs before freeing the stack frame, but the returned `samr_Password` copies remain caller-owned.

## Dependencies and Integration Points

The file sits between DSDB/LDB search helpers, generated LSA/DRS NDR structures, DNS comparison helpers, LSARPC forest trust conversion helpers, security/claims code, and crypto helpers. It is consumed by trust RPC implementations, forest-trust scanning, authentication/routing logic, and claims transformation enforcement.

## Risks

The main behavioral risk is compatibility with Windows forest-trust semantics. List order, duplicate retention, disabled flags, and collision indexes are observable through LSA APIs. DNS comparison uses `dns_cmp()` and must preserve case-normalized values without allowing malformed names. Trust password parsing handles secret material and must avoid lifetime mistakes or accidental logging. Routing lookups are security-sensitive because an incorrect best TLN or disabled-flag interpretation can send authentication or authorization traffic to the wrong trust.

## Test Signals

Useful tests include forest trust normalization with trailing dots, duplicates, TLN/TLN_EX hierarchy violations, scanner-info records, admin-disabled records, SID/NetBIOS collisions, and Windows trace-compatible ordering. Routing tests should cover exact NetBIOS, exact DNS, child DNS best-match, disabled TLN/SID/NB flags, non-transitive trusts, downlevel trusts, and missing forest trust blobs. Secret tests should cover `trustAuthIncoming` with NTOWF, cleartext, previous-missing fallback, corrupt NDR, and absent attributes. Claims policy tests should cover DN containment, missing rules, malformed XML/rules, and non-policy objects.
