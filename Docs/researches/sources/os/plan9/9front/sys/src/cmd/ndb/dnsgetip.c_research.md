# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnsgetip.c

One-shot resolver that prints IP addresses for a domain.

Key elements:
- Supports `-a` for all addresses, `-d` debug, and `-x` for `/net.alt`.
- Runs in resolver mode with `cfg.resolver = 1`.
- `resolve` wraps `dnresolve` for A or AAAA, strips negative entries, prints `rp->ip->name`, and exits early unless `-a` is set.
- Main resolves both IPv4 and IPv6 unless the input is already an IP literal.
- Provides standalone stubs for `syslog`, `logreply`, and `logrequest`.

Notable behavior:
- Uses `req.isslave = 1` to avoid worker forking.
- If no addresses are found, reports separate v4/v6 failure strings when they differ.

Risks and quirks:
- `resolve` calls `exits(nil)` inside the RR loop when not `-a`, so normal cleanup after the first address is skipped by process exit.
