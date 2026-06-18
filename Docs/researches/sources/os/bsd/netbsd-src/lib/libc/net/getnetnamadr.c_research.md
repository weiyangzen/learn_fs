# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getnetnamadr.c

Read completely: 651 lines.

This file implements `getnetbyaddr` and `getnetbyname` using `nsdispatch` over files, DNS, and optional NIS. It shares `_net_stayopen` state with `getnetent.c` and stores returned `netent` data in static structures.

Files backends scan `getnetent`. DNS backends construct RFC1101-style `in-addr.arpa` PTR queries for networks, parse DNS responses with `getnetanswer`, validate names with resolver policy, and derive network numbers from reversed names. Optional YP backends query `networks.byaddr` and `networks.byname`.

Security/reliability notes: DNS answer parsing uses static buffers and manual pointer traversal; malformed compressed names or unexpected record layouts set `h_errno` and return not found/unavailable. The APIs are not thread-safe because returned structures and alias arrays are static.
