# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_parser.c

## Purpose
Core helper implementation for `pfctl` parsing, display, address expansion, interface lookup, and PF transaction buffer handling.

## Main Elements
- Defines ICMP/ICMPv6 type and code name tables and PF timeout name mappings.
- Pretty-printers for rules, ethernet rules, pools, status, source nodes, tables, state/source limiters, ports, uid/gid clauses, flags, labels, NAT/RDR/binat pools, scrub options, queue/tag options, route options, divert options, and expired rules.
- Host and interface expansion: `host()`, `host_ip()`, `host_if()`, `host_dns()`, `ifa_load()`, `ifa_lookup()`, group lookup, dynamic nodes, netmask handling, and address-list conversion.
- Interface-group cache using `hsearch_r()` initialized by constructor.
- PF table address append helpers and transaction helpers: `append_addr()`, `append_addr_host()`, `pfctl_add_trans()`, `pfctl_get_ticket()`, `pfctl_trans()`.

## Dependencies And Integration
Uses kernel PF structures from `<net/pfvar.h>`, interface ioctls, `getifaddrs()`, `getaddrinfo()`, libpfctl-facing structs, and declarations from `pfctl_parser.h`/`pfctl.h`. Other pfctl modules rely on this file for printable rule output and parser-time host/table expansion.

## Risk Notes
The code mixes user-visible formatting with kernel ABI fields. Address-family handling, interface-group lookup, netmask truncation, and list expansion are high-risk areas because parser output must match kernel expectations and regression `.ok` files exactly.
