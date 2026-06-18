# sources/user-network-fs/samba/source3/utils/net_lookup.c

## Purpose
This file implements `net lookup`, a resolver-oriented command family for NetBIOS names, LDAP/DC/KDC discovery, master browser lookup, SID/name conversion, and `DsGetDcName` diagnostics.

## Important APIs, Types, And Control Flow
`net_lookup()` dispatches subcommands `HOST`, `LDAP`, `DC`, `PDC`, `MASTER`, `KDC`, `NAME`, `SID`, and `DSGETDCNAME`, defaulting unknown first words to host lookup for compatibility with `name#type` syntax. `net_lookup_host()` parses optional NetBIOS type suffixes and calls `resolve_name()`. LDAP lookup, when ADS is available, queries DNS SRV records with sitename support and falls back through PDC discovery. DC/PDC/master lookup use `get_pdc_ip()`, `get_sorted_dc_list()`, and `find_master_ip()`. KDC lookup initializes a Kerberos context and prints realm KDCs. SID/name commands call `lookup_name()` and `lookup_sid()`. `net_lookup_dsgetdcname()` calls `dsgetdcname()` and NDR-prints the returned `netr_DsRGetDCNameInfo`.

## State And Persistence
This file performs network and cache lookups but does not write persistent state. It may read Samba configuration, site-name cache, DNS, NetBIOS browse state, passdb/name-service data, and message context state for `dsgetdcname`.

## Dependencies And Integration Points
Dependencies include namequery, ADS DNS SRV helpers, site-name cache, Kerberos support, security/SID helpers, passdb lookup, generated Netlogon NDR types, and dsgetdcname. Feature guards return errors when ADS or Kerberos support is not compiled in.

## Risks And Test Signals
`net_lookup_host()` mutates the supplied argument string at `#`, so argv mutability assumptions matter. LDAP fallback recomputes `domain` from PDC DNS name but reuses the original DNS query string, which is worth regression coverage. `dsgetdcname` requires `c->msg_ctx` and reports root/messaging issues. Test IPv4/IPv6 formatting, `name#type`, ADS-disabled and Kerberos-disabled builds, site-specific LDAP lookup, DC de-duplication of PDC address, SID/name failures, and flag parsing for `dsgetdcname`.
