# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfstat/ipfstat.c

`ipfstat.c` implements the IPFilter status and inspection command. It opens the filter, state, auth, and NAT device nodes for live inspection, or switches to crash-dump/kernel-memory mode with `-M`/`-N`. It verifies user/kernel version compatibility, drops elevated privileges after opening privileged resources, and retrieves `friostat_t`, `ips_stat_t`, `ipfrstat_t`, and `ipf_authstat_t` through ioctls or symbol-table/kmem copies.

Major behaviors:
- Prints global filter counters, packet log flags, block reasons, fastroute counters, pullup/coalesce/checksum counters, and IPv4/IPv6 packet totals.
- Lists active/inactive filter and accounting rules, including hits, bytes, line numbers, nested groups, callfunc rules, and optional binary debug dumps.
- Lists or summarizes state table entries, including custom field output via `parsefields`, expression filtering via `parseipfexpr`, and bucket distribution statistics.
- Shows fragment cache entries for filter and NAT fragment tables.
- Shows auth queue statistics and pending auth entries.
- Shows configured filter/accounting/auth groups.
- When compiled with `STATETOP`, provides a curses top-like live state view with source/destination/protocol/port filters, sorting by protocol/packets/bytes/TTL/source/destination, reverse ordering, refresh interval, resize handling, and closed-TCP suppression.

Notable implementation details:
- Live iteration uses `SIOCGENITER`, `SIOCIPFITER`, `SIOCIPFDELTOK`, `SIOCGTABL`, and related object wrappers (`ipfobj_t`, `ipfgeniter_t`).
- Dead-kernel support depends on hard-coded symbol names such as `frstats`, `ips_stats`, `ipfr_stats`, `ipf_rules`, `ipf_acct`, and `ipf_state_logging`.
- `state_matcharray()` evaluates parsed filter expressions against `ipstate_t` fields for protocol, IPv4/IPv6 addresses, TCP/UDP ports, idle time, and TCP states.
- Several code paths are diagnostic and trust kernel/core structures heavily; failures usually print and exit or silently stop iteration.
