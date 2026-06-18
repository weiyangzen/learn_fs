# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_findzonecut.c

Read completely: 723 lines.

Finds the enclosing DNS zone cut and authoritative server addresses for a name/class. `res_findzonecut()` is the IPv4 wrapper; `res_findzonecut2()` supports `union res_sockaddr_union`, IPv4/IPv6 filtering, and exhaustive glue lookup.

The algorithm canonicalizes the input name, queries for SOA records while stripping labels upward, saves the zone name and SOA MNAME, collects NS records from answer/authority sections, saves additional-section A/AAAA glue, and queries missing A/AAAA glue when necessary. It prefers the SOA MNAME server address, then other NS addresses.

The implementation assumes a functional recursive resolver and does not handle referrals itself. It treats unexpected CNAME/DNAME results as failure or as a signal to continue searching, and manages temporary RRsets with tail queues.
