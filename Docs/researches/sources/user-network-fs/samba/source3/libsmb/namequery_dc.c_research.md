# sources/user-network-fs/samba/source3/libsmb/namequery_dc.c

## Purpose
This file provides `get_dc_name`, a domain-controller name and address selector. It prefers ADS/CLDAP discovery when appropriate, handles site-aware Kerberos configuration for the local domain, and falls back to NetBIOS/RPC-style DC discovery through `get_sorted_dc_list` plus node status.

## Important APIs, Types, And Functions
The exported function is `get_dc_name`. Internal helpers are `is_our_primary_domain` under `HAVE_ADS`, `ads_dc_name`, and `rpc_dc_name`. The code works with `ADS_STRUCT`, `fstring` server names, `struct sockaddr_storage`, loadparm role/security/realm/workgroup settings, and namequery helpers.

## Control Flow
`get_dc_name` zeroes the output address and decides whether the requested domain/realm is the local domain. If local ADS security is active or a realm is supplied, it tries `ads_dc_name`. ADS discovery initializes an ADS context, does CLDAP-only connection, reacts to closest-site changes by clearing related `0x1c` namecache entries and retrying up to three times, uppercases the LDAP server name, and returns the LDAP socket address. For local domains with a KDC response, it writes a private krb5 configuration targeting the selected KDC and site.

If ADS discovery is not applicable or fails and a NetBIOS domain is available, `get_dc_name` calls `rpc_dc_name`. That function asks `get_sorted_dc_list` for DC addresses, does `name_status_find(domain, 0x1c, 0x20, ...)` to convert a DC IP to a server NetBIOS name, skips negative connection-cache entries, and returns the first usable name/address.

## State And Persistence
The ADS path can update local site/Kerberos configuration through `create_local_private_krb5_conf_for_domain`. It can also invalidate namecache entries for realm/domain `0x1c` when site information changes. The RPC path reads negative connection-cache state but does not write persistent state directly.

## Dependencies And Integration Points
This file integrates ADS discovery (`ads_init`, `ads_connect_cldap_only`, `ads_closest_dc`), sitename cache, loadparm, namecache invalidation, `get_sorted_dc_list`, node status lookup, and negative connection cache. It is a bridge from generic name resolution to callers that need both the DC name and socket address.

## Risks And Edge Cases
When `domain` is `NULL`, ADS is the only possible path and failure returns false. Repeated site changes abort after three attempts. Builds without `HAVE_ADS` compile stubs for ADS-dependent address selection and leave `dc_ss` zeroed if no fallback exists. RPC fallback depends on NetBIOS node status and therefore IPv4/NBT availability. Negative connection cache entries can hide otherwise resolvable DCs.

## Test Signals
Tests should cover local ADS domain selection, explicit realm lookup, site-change retry and cache deletion, KDC krb5 config generation for closest DCs, ADS failure followed by RPC fallback, negative connection-cache filtering, no-domain realm-only failure, and non-ADS builds.
