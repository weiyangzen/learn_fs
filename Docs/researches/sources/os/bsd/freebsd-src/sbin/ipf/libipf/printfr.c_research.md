# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printfr.c

Main IPFilter rule pretty-printer.

Key behavior:
- Reconstructs readable rule text from `frentry`.
- Prints action, return behavior, direction, logging, quick flag, interfaces, `to`/`dup-to`/`reply-to`, fastroute, family, protocol, addresses, ports, ICMP type/code, TCP flags, BPF, callfunc, and expression filters.
- Prints `with` clauses for packet flags and IPv4/IPv6 options.
- Prints keep-state/keep-frag settings, scan/group/head, tags, pps, comments, state counts, TTL, and debug refcounts.

Research notes:
- Calls `kvatoname()` to resolve kernel function pointers for call rules.
- Output is tightly coupled to packed name offsets inside `frentry`.
