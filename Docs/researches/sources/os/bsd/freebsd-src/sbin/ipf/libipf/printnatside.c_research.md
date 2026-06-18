# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printnatside.c

NAT per-side statistics printer.

Key behavior:
- Prints counters for proxy failures, bad NAT cases, buckets, clone failures, decapsulation, divert, drops, exhaustion, ICMP handling, insert/lookup misses, memory failures, translations, wraps, and null/existing translations.
- Verbose mode prints the table pointer.

Research notes:
- `ns_memfail` is printed twice with different labels.
