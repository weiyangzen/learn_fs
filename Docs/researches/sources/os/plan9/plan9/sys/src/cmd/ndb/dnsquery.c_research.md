# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnsquery.c

Interactive client for `/net/dns`. It mounts `/srv/dns` if `/net/dns` is unavailable, writes queries to the DNS 9P file, seeks back, and prints all returned chunks.

Input defaults to `ip` queries for names and `ptr` for numeric IPs. IPv4 PTR input without `.arpa` is rewritten into `in-addr.arpa ptr`; IPv6 reverse conversion is explicitly TODO. `-x` switches to `/net.alt/dns` and `/srv/dns_net.alt`.

The file is operational glue rather than resolver logic. It depends on the daemon’s 9P protocol and on `ipattr()` to distinguish numeric addresses.

Risks are small: fixed 1024-byte buffers, simple whitespace trimming, and no parsing of structured RR output.
