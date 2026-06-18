<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_util.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_util.c

## Purpose
This is a core utility file for winbind domain and client management. It owns the trusted-domain list, domain references, trust rescans, domain lookup/routing helpers, username parsing/canonicalization, client list bookkeeping, cached group lookup, name normalization, KDC locator environment setup, auth error formatting, online/offline checks, and SID/XID list parsers.

## Important APIs, Types, And Functions
Domain-list APIs include `domain_list()`, `wb_next_domain()`, `_winbindd_domain_ref_set/get()`, `add_trusted_domain_from_auth()`, `domain_is_forest_root()`, `rescan_trusted_domains()`, `update_trusted_domains_dc()`, `init_domain_list()`, and the `find_*domain*` helpers. Client APIs include `winbindd_client_list()`, `winbindd_add_client()`, `winbindd_remove_client()`, `winbindd_promote_client()`, and `winbindd_num_clients()`. Identity helpers include `parse_domain_user()`, `canonicalize_username()`, `fill_domain_username_talloc()`, `lookup_usergroups_cached()`, `normalize_name_map()`, `normalize_name_unmap()`, `parse_sidlist()`, `parse_xidlist()`, and `find_dns_domain_name()`.

## Control Flow
`domain_list()` lazily initializes global domain state through `init_domain_list()`. `add_trusted_domain()` validates uniqueness of SID and DNS names, creates `winbindd_domain` objects, initializes child connection structures and routing metadata, adds entries to the global list, bumps `domain_list_generation`, and updates the trusted-domain cache. Trust rescans call child `ListTrustedDomains` requests asynchronously, add newly discovered trusts, and follow forest root and forest-transitive trust paths. Lookup helpers route SIDs and names differently for member servers versus DCs, handling local SAM, BUILTIN, Unix pseudo-domains, well-known domains, and default route domains.

## State And Persistence Behavior
The file owns `_domain_list`, `domain_list_generation`, `_client_list`, and `_num_clients`. It reads and updates the winbind trusted-domain cache, migrates secrets database formats, sends process messages for new trusted domains, starts/stops domain children, and may set/unset environment variables used by the Kerberos locator plugin. Per-domain state includes online/offline flags, routing domain pointers, child arrays, queues, trust flags, and cached sequence/connection metadata.

## Dependencies And Integration Points
It depends on Samba configuration, secrets, passdb, machine SID, LSA trust structures, DRS blobs, messaging, global event contexts, samlogon cache, SID utilities, string parsing, idmap types, and winbind child RPC interfaces. It is integrated almost everywhere in winbindd: backend selection, NSS request parsing, trust discovery, client lifecycle, offline/online behavior, and batch ID mapping command parsing.

## Risks And Test Signals
This file has high blast radius. Risks include stale domain pointers after rescans, trust-cache drift when removed domains remain until restart, duplicate SID/DNS validation errors, member/DC routing differences, username parsing around separators and UPNs, normalization alias lookup marking domains offline, and parser strictness for newline/null-terminated SID/XID lists. The checked-out source also contains duplicate-looking lines in a few places, making full compile coverage important. Strong signals are domain initialization on standalone/member/DC roles, trust rescans including forest trusts, auth-driven on-the-fly domain addition, SID/name routing tests, default-domain username parsing, client list accounting, and invalid list parser tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_util.c -->
