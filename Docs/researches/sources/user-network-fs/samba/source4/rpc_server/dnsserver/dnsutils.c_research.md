# sources/user-network-fs/samba/source4/rpc_server/dnsserver/dnsutils.c

Purpose: initialization and lookup utilities for DNS RPC server state.

Important APIs and control flow: `fill_dns_addr_array()` builds `DNS_ADDR_ARRAY` data from configured Samba interfaces for listen addresses, supporting IPv4, IPv6, or mixed family. `dnsserver_init_serverinfo()` composes server-wide MS-DNSP properties from DCE/RPC server version info, loadparm DNS hostname/domain, samdb naming contexts, functional levels, listener addresses, and default DNS settings. `dnsserver_init_zoneinfo()` derives reverse-zone status, root-hints/cache behavior, primary-zone defaults, and applies parsed `dNSProperty` blobs through `dns_zoneinfo_load_zone_property()`. `dnsserver_find_zone()` compares names with Samba DNS equality. `dnsserver_name_to_dn()` builds child `DC=` DNs, mapping a zone name to `DC=@`. `dnsserver_zone_to_request_filter()` maps pseudo-zone names like `..AllZones` to request filter bitmasks.

State and persistence: no direct writes. It initializes talloc-owned server and zone info from configuration and samdb metadata.

Dependencies and integration: used during DNS RPC connection setup and zone mutations. Depends on interface enumeration, IP parsing, SAMDB naming context helpers, DNS common property loader, and common RPC loadparm version helper.

Risks and test signals: interface address encoding and pseudo-zone filters must match MS-DNSP expectations. Tests should cover no interfaces, IPv4/IPv6/mixed listeners, root zone defaults, reverse-zone detection, malformed zone properties, and each pseudo-zone request filter.
