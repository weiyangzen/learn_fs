# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/parse.y

This is the yacc grammar, lexer, macro processor, and semantic rule-expansion core for `pfctl` configuration files.

Key responsibilities:
- Parses `pf.conf` syntax into PF rules, anchors, tables, queues, options, state/source limiters, antispoof rules, and deferred anchor loads.
- Implements the scanner for keywords, strings, quoted strings, comments, numbers, operators, macros, and include files.
- Tracks parser file stack, line numbers, unget buffers, EOF behavior, and nested includes.
- Supports macro assignment and expansion with command-line persistent macros.
- Converts parsed rule syntax into `struct pf_rule`, queue specs, table definitions, limiter definitions, and PF option calls.
- Expands list syntax into cross-product rule combinations across interfaces, protocols, hosts, ports, users, groups, OS fingerprints, and ICMP types.
- Validates rule consistency before inserting expanded rules.
- Handles inline brace anchors by temporarily parsing into generated internal anchors and moving rules/tables to the final anchor path.
- Defers `load anchor ... from ...` statements for later loading.
- Parses and applies NAT, rdr, binat, af-to, route-to, reply-to, dup-to, divert, scrub, tag, label, queue, probability, TOS, prio, delay, and state options.

Major grammar areas:
- Top-level `ruleset` accepts includes, options, state/source limiters, filter rules, anchor rules, load rules, queue specs, variable assignments, antispoof rules, table definitions, and inline anchors.
- `option` handles `set` directives: reassembly, optimization, ruleset optimization, timeouts, limits, loginterface, hostid, block-policy, fingerprints, state-policy, debug, skip, state-defaults, and syncookies.
- `anchorrule`, `pfa_anchor`, and `loadrule` handle named anchors, inline anchors, and deferred anchor-file loads.
- `tabledef` and `table_opts` parse table flags, inline addresses, and file-backed table initialization.
- `queuespec`, `queue_opts`, `scspec`, and `bandwidth` parse HFSC/FQ-style queue definitions.
- `statelim` and `sourcelim` define named/id-based limiters with limits, rates, table thresholds, entries, and address masks.
- `pfrule` builds pass/block/match rules and applies state defaults, TCP flag defaults, state tracking, adaptive timeouts, routing, and divert handling.
- `filter_opts` collects user/group, flags, ICMP, priority, TOS, state, fragment, label, queue, tags, probability, limiters, rtable, divert, scrub, NAT/rdr/binat/af-to, route handling, received-on, once, and max-packet-rate options.
- `host`, `dynaddr`, `portspec`, `uids`, `gids`, `flags`, `icmpspec`, and `tos` parse address and match primitives.

Important semantic functions:
- `parse_config()` initializes parser globals, pushes the main config file, runs `yyparse()`, pops files, frees macros, and reports success/failure.
- `pfctl_cmdline_symset()`, `symset()`, and `symget()` implement macro storage, persistent command-line definitions, and usage tracking.
- `pushfile()` and `popfile()` manage the include stack.
- `check_file_secrecy()` verifies ownership and permissions for secret files when requested.
- `yylex()`, `lgetc()`, `igetc()`, `lungetc()`, and `findeol()` implement lexical scanning, macro-expansion pushback, continuation lines, comments, quoted strings, and error recovery.
- `lookup()` maps reserved words to yacc tokens through a sorted keyword table.
- `process_tabledef()` loads table addresses from files/hosts, defines tables, and postpones non-root table materialization for anchor path resolution.
- `expand_queue()` converts parsed queue options into `pf_queuespec` entries.
- `filteropts_to_rule()` copies parsed filter options into a `struct pf_rule` and enforces option-specific constraints.
- `expand_rule()` performs the main cross-product expansion and calls `pfctl_add_rule()`.
- `collapse_redirspec()` turns translation/routing address pools into a rule pool or generated table.
- `apply_redirspec()` applies proxy ports, pool type, source-hash keys, sticky-address, and static-port behavior.
- `rule_consistent()` enforces protocol/action/address-family constraints.
- `expand_divertspec()` validates and applies divert options.
- `expand_label*()` expands `$if`, `$srcaddr`, `$dstaddr`, `$srcport`, `$dstport`, `$proto`, and later `$nr`.
- `mv_rules()` and `mv_tables()` move inline-anchor rules and tables from temporary anchors to final anchors.
- `lookup_rtable()` verifies route table IDs via `sysctl`.
- `parseport()`, `getservice()`, `parseicmpspec()`, `map_tos()`, and `atoul()` parse service names, numeric ports, ICMP codes, TOS/DSCP names, and numeric strings.

Notable behavior:
- Pass rules default to `keep state` unless explicitly changed.
- Stateful TCP rules default to `flags S/SA` unless flags are specified or the rule is fragment-only.
- `modulate state` and `synproxy state` degrade to normal state for non-TCP protocol expansions.
- `route-to`, `reply-to`, and `dup-to` require state and, except `dup-to`, require an explicit direction.
- `nat-to` and `rdr-to` require state except on match rules, and also require a direction.
- `af-to` is only accepted on inbound rules and cannot be combined with route handling.
- `binat-to` expands into outbound NAT plus a generated inbound rdr rule.
- Tables and multi-address dynamic interfaces are disallowed for pool types that cannot support them.
- Multiple translation/routing addresses may be converted into optimizer-generated tables.
- Dynamic interface addresses support modifiers such as `:network`, `:broadcast`, `:peer`, and `:0`; incompatible modifier combinations are rejected.
- `@if` host syntax is explicitly rejected in ordinary `from`/`to` and translation/routing contexts.
- ICMP type/code rules require an address family and must match ICMP/ICMPv6 protocol selection.
- `allow-opts` is pass-only; keep state is pass-only; routing is unsupported on block/match where invalid.
- IPv6 rejects scrub options that only apply to IPv4, such as `no-df` and `random-id`.
- State limiter and source limiter references are pass-only.
- Source tracking options reject incompatible global/rule-scoped combinations.
- Labels and tags can interpolate rule attributes before insertion, while `$nr` is expanded after optimization.
- Includes and macros are integrated at lexer level, so grammar productions see expanded token streams.

Dependencies:
- Uses `pfctl_parser.h` and `pfctl.h`.
- Consumes many PF kernel ABI structures and constants from `net/pfvar.h`.
- Calls PF control helpers such as `pfctl_set_*`, `pfctl_add_rule`, `pfctl_define_table`, `pfctl_add_queue`, `pfctl_rules`, limiter helpers, table helpers, and optimizer/table support.
- Uses libc resolver/user/group/service APIs, `sysctl`, MD5, random key generation, and OpenBSD queue/tree macros.

Research notes:
- This file is the main semantic bridge between human `pf.conf` syntax and the internal PF ruleset representation.
- Changes here affect both accepted syntax and the exact rule expansion sent to the kernel, especially around anchors, tables, NAT/rdr/af-to, and state defaults.
