# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/parse.y

## Purpose
Yacc grammar and support implementation for parsing FreeBSD `pfctl` configuration files. It translates `pf.conf` syntax into in-memory `pfctl` rules, anchors, tables, ALTQ queue definitions, Ethernet rules, NAT/rdr/binat translation rules, state/source limiters, and global PF options before handoff to the pfctl load paths.

## Main Elements
- Parser prologue defines parser-global state: active `struct pfctl *pf`, current rule-order state, default block/fail policies, default ICMP return values, macro table, include-file stack, ALTQ queue staging list, state-default list, and reusable option accumulator structs.
- Grammar entry `ruleset` accepts includes, options, state/source limiter declarations, Ethernet rules, scrub rules, NAT/binat/rdr rules, filter rules, anchors, ALTQ/queue definitions, variables, antispoof rules, and tables.
- `option` handles `set` directives: reassembly, optimization, ruleset optimization, timeouts, limits, loginterface, hostid, block/fail policy, require-order, fingerprints, state-policy/defaults, debug level, skip interfaces, keepcounters, and syncookies.
- Rule grammars build `struct pfctl_rule` or `struct pfctl_eth_rule` for `pass`, `match`, `block`, `scrub`, `antispoof`, `nat`, `rdr`, `binat`, `nat-to`, `rdr-to`, `binat-to`, `af-to`, `route-to`, `reply-to`, and `dup-to`.
- Support routines include consistency checks, table processing, label macro expansion, combinatorial rule expansion, pool application, binat-to companion rule generation, skip-interface application, lexer/token lookup, include-file management, macro management, and parser entry `parse_config()`.

## Dependencies And Integration
Uses `pfctl_parser.h`, `pfctl.h`, `<net/pfvar.h>`, ALTQ headers, libc name-service helpers, sysctl, MD5, and pfctl helper functions such as `pfctl_append_rule()`, `pfctl_define_table()`, `pfctl_add_altq()`, `pfctl_set_*()`, `host()`, `ifa_lookup()`, and `gen_dynnode()`.

## Risk Notes
This is a high-blast-radius parser: grammar changes can silently alter pf.conf compatibility, rule ordering, or generated kernel rule semantics. Parser-global accumulator structs, inline anchor/table movement, and address-family inference around NAT/rdr/binat are especially subtle.
