# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dblookup.c

Implements DNS resource-record lookup from Plan 9 ndb databases and database-backed DNS cache maintenance.

Key responsibilities:
- Opens and combines the configured ndb file with `/net/ndb` when present.
- `dblookup` handles class/type dispatch, `Tall` expansion, cached vs uncached lookup, wildcard domain search, and DNS response-code annotation for missing names.
- `dblookup1` maps DNS RR types to ndb attributes and RR constructors for A, AAAA, CNAME, MX, NS, PTR, SOA, SRV, TXT, CAA, AXFR/IXFR stubs, and wildcard/case/IDN lookup variants.
- Searches ndb by `dom` and, for single-label names, `sys`; tries IDN/UTF and lower-case variants.
- Respects line-level binding before whole-entry binding when associating attributes.
- Builds RR objects for addresses, text strings, aliases, MX/NS/SOA/SRV/CAA, and default TTL/serial values.
- Reads database contents into the DNS cache when `cfg.cachedb` is enabled, attaches authoritative and database RRs, and refreshes when source files change.
- Maintains local domain information via `lookupinfo`, interface scanning, and `mydoms`.
- Detects bad delegations to local DNS names outside owned areas.
- Determines whether IPs are local or on local networks.
- Builds synthetic local DNS server NS/A/AAAA records from `DOTSERVER`, `DNSSERVER`, `@dot`, and `@dns` configuration while rejecting self/duplicate/bad addresses.
- Builds domain search-list PTR records from `dnsdomain`.
- Generates reverse PTRs for owned IPv4 `in-addr.arpa` and IPv6 `ip6.arpa` areas, including classless IPv4 reverse handling and IPv6 nibble-prefix conversion.

Important interactions:
- Uses global DNS configuration/state such as `cfg`, `now`, `owned`, `delegated`, `Area`, `DN`, and RR cache helpers.
- Depends on ndb parsing/searching, IDN conversion, IP interface inspection, and DNS RR allocation/attachment routines.

Notable quirks:
- `doaxfr` is a stub here because TCP-specific transfer handling answers it elsewhere.
- Generated PTR TTL is deliberately nonzero to avoid resolver confusion with zero-TTL PTRs.
- Database reload loops until observed modification times are stable enough for a consistent cache read.
