# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.c

`pfctl_parser.c` is shared parser support rather than the grammar itself. It provides symbolic ICMP/log/timeouts lookup, rule/status/source/queue/table printing, TCP flag parsing, address and interface resolution, netmask handling, address-buffer appending, and PF transaction helpers used by the grammar and main command code.

Primary responsibilities:
- Defines ICMP/ICMPv6 type and code name tables.
- Defines `pf_timeouts[]`, the canonical string-to-timeout mapping used by set/show timeout paths.
- Implements printable reconstruction of PF kernel structs: rules, pools, state/source limiters, source nodes, status, queue specs, and table definitions.
- Implements host/interface/DNS address resolution into `struct node_host` lists.
- Converts `node_host` lists into PF table address buffers through `append_addr()` and `append_addr_host()`.
- Provides transaction buffer helpers `pfctl_add_trans()`, `pfctl_get_ticket()`, and `pfctl_trans()`.

Printing behavior:
- `print_rule()` reconstructs a rule in pf.conf-like syntax, covering action, anchor calls, return behavior, direction, logging, quick, interface/rdomain, AF, protocol, from/to, ports, OS fingerprint, UID/GID, flags, ICMP type/code, TOS, priority, packet rate, set clauses, state options, probability, state/source limiters, scrub options, labels, tags, rtable, divert, NAT/RDR/af-to, and route/reply/dup-to.
- `print_status()` formats runtime, hostid/checksum, interface counters, state/source/fragments/counters/limit counters, and syncookie watermarks.
- `print_src_node()`, `print_statelim()`, `print_sourcelim()`, `print_tabledef()`, and `print_queuespec()` provide focused formatters for PF subobjects.
- Service names are used for ports only when `PF_OPT_PORTNAMES` is set.

Address/interface handling:
- `set_ipmask()` builds IPv4/IPv6 masks and masks address bits.
- `check_netmask()` validates IPv4 masks do not exceed 32 bits.
- `gen_dynnode()` clones dynamic interface table nodes and clamps IPv4 masks.
- `ifa_load()` snapshots `getifaddrs()` into `iftab`, including AF_LINK indexes, IPv4/IPv6 addresses, netmasks, broadcast, peer, and scope ids.
- `ifa_exists()` checks both real interfaces and interface groups via `SIOCGIFGMEMB`.
- `ifa_grouplookup()` expands interface groups by recursively resolving members.
- `ifa_lookup()` resolves interface selectors, `self`, broadcast/peer/network/noalias modifiers, and prefix matching for interface families.
- `host()` attempts interface lookup, numeric IP parsing, then DNS lookup unless numeric/no-DNS mode is requested.
- `host_ip()` supports both normal numeric addresses and IPv4 network shorthand such as `10/8`.
- `host_dns()` supports `:0` no-alias selection.

Integration points:
- `parse_config()` and `pfctl_load_anchors()` are declared elsewhere but depend on these helpers.
- `pfctl.c` uses the print helpers for show paths, option setters for parser actions, and transaction helpers for load/clear operations.
- `pfctl_radix.c` calls `append_addr()` through `pfr_buf_load()`.
- `pfctl_optimize.c` uses `append_addr_host()`, `unmask()`, and `print_tabledef()`.
- OS fingerprint printing uses `pfctl_lookup_fingerprint()`.

Notable risks and edge cases:
- `append_addr()` uses static state to apply a following `weight` token to addresses added by the previous call; callers must preserve token order.
- Interface-group expansion and `self` can produce many addresses and mixes IPv4/IPv6 depending on system state.
- DNS lookup behavior is controlled by parser options; reproducibility differs between `PF_OPT_NODNS`, numeric mode, and default mode.
- Many functions allocate linked `node_host` lists; callers usually free only simple lists or rely on process exit.
