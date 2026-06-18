# sources/user-network-fs/samba/source3/libsmb/dsgetdcname.c

## Purpose

This file implements Samba's `DsGetDcName`-style domain-controller discovery. It resolves DC candidates by DNS SRV and/or NetBIOS, probes them with CLDAP/netlogon pings or NetBIOS datagrams, maps replies to `netr_DsRGetDCNameInfo`, caches successful discoveries, and supports targeted discovery of one named DC.

## Important APIs, Types, and Functions

Public APIs are `dsgetdcname()` and `dsgetonedcname()`. Important internals include `check_allowed_required_flags()`, `discover_dc_dns()`, `discover_dc_netbios()`, `process_dc_dns()`, `process_dc_netbios()`, `make_dc_info_from_cldap_reply()`, `make_domain_controller_info()`, `map_dc_and_domain_names()`, `map_ds_flags_to_nt_version()`, `dsgetdcname_rediscover()`, and `is_closest_site()`. `struct ip_service_name` pairs a Samba socket address with a hostname.

## Control Flow

`dsgetdcname()` validates flag combinations, derives a site from the site cache when none is provided, builds a gencache key from domain/guid/site/flags, and returns a cached NDR-decoded info struct unless forced rediscovery is requested. If discovery is needed, `dsgetdcname_rediscover()` chooses DNS for DNS names, NetBIOS for flat names, or DNS with NetBIOS fallback for unspecified names. DNS discovery builds SRV queries for PDC/GC/KDC/DC/guid cases, keeps up to one IPv4 and one IPv6 address per SRV target, then probes with `netlogon_pings()`. NetBIOS discovery resolves logon or PDC names and uses `nbt_getdc()` with AD-style response flags, falling back to `name_status_find()` for older responses. Successful non-closest-site results can trigger a second discovery against the client site from the first reply.

## State and Persistence Behavior

Successful results are cached in `gencache` for 15 minutes as NDR `netr_DsRGetDCNameInfo` blobs under `DSGETDCNAME/...` keys. The client site is stored through `sitename_store()`. Name cache entries are updated for NetBIOS results. No permanent local files are written by this file directly.

## Dependencies and Integration Points

The file integrates with DNS SRV query builders, async DNS timeout settings, CLDAP/netlogon ping code, NetBIOS name resolution and datagrams, sitename cache, gencache, tsocket address conversion, loadparm options such as `lp_disable_netbios()` and `lp_ldap_timeout()`, and generated NDR netlogon structures.

## Risks and Test Signals

Risks include invalid flag combinations, stale cache entries, DNS records without addresses, IPv6/IPv4 address conversion failures, site fallback loops, NetBIOS disabled behavior, pause responses from netlogon, and mapping flat versus DNS names incorrectly. Tests should cover cache hit/miss/invalid-NDR eviction, `DS_FORCE_REDISCOVERY`, `DS_BACKGROUND_ONLY`, flat-only and DNS-only discovery, PDC/GC/KDC flags, site-specific retry, closest-site replacement, single-DC discovery, and DNS/NetBIOS failure fallbacks.
