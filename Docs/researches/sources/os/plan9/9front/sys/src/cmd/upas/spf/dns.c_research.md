# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/dns.c

`dns.c` wraps DNS lookups for the SPF tool. `vdnsquery()` applies a 15-second alarm timeout, debug logging, recursion/query count limits, and delegates to `dnsquery()` under `netroot`.

It also provides `dnreverse()` for IPv4 reverse lookup names and `dncontains()` for suffix-style domain containment checks. The query limits differ from strict SPF spec comments but prevent runaway DNS recursion.
