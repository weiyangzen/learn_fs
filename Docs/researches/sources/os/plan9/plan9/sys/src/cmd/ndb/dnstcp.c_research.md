# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnstcp.c

Standalone TCP DNS server process, intended to be run for a single TCP connection. It reads length-prefixed DNS messages from stdin, answers normal queries via `dnserver()`, and handles AXFR zone transfers directly.

`main()` parses resolver/no-recursion/db/net options, initializes DNS cache, reads caller address from an optional connection directory, loads DB cache, then loops over TCP DNS messages with long request abort time. Each question is handled as either `Taxfr` via `dnzone()` or normal `dnserver()` plus `reply()`.

`dnzone()` streams AXFR by sending SOA first, then walking the global DN hash table breadth-first by label depth for records in-zone, skipping negative and SOA records, and finally sending SOA again. It uses cached DB contents, so `cfg.cachedb` is enabled.

On exit, `refreshmain()` writes `refresh` to the main `/net/dns` file. Risks include direct traversal of global `ht`, shallow copying RR structs for zone streaming, and broad reliance on cache already being authoritative/current.
