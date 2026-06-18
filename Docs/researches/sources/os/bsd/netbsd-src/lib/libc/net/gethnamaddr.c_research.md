# File Research: sources/os/bsd/netbsd-src/lib/libc/net/gethnamaddr.c

Read completely: 1364 lines.

This file implements traditional host database APIs and their reentrant forms: `gethostbyname_r`, `gethostbyname2_r`, `gethostbyaddr_r`, `gethostent_r`, and non-reentrant `gethostbyname`, `gethostbyname2`, `gethostbyaddr`, and `gethostent`. It also provides DNS backend callbacks `_dns_gethtbyname` and `_dns_gethtbyaddr`, with optional YP callbacks when compiled with `YP`.

`getanswer` parses DNS A, AAAA, PTR, and CNAME responses into caller-provided `hostent` buffers, validates names with resolver policy, stores aliases/address lists, sorts IPv4 addresses by resolver sortlist, supports multiple PTRs as aliases, and maps IPv4 results to IPv4-mapped IPv6 when `RES_USE_INET6` is set. Name lookups detect numeric IPv4/IPv6 strings and synthesize hostents without DNS; address lookups unmap v4-mapped/v4-compatible IPv6 and reject link/site-local reverse lookups.

`gethostent_r` parses `_PATH_HOSTS` lines with `fparseln`, supports IPv4 and IPv6 literals, gathers aliases dynamically, and copies all result data into the provided buffer through hostent-copy macros. YP helpers parse `hosts.byname`, `hosts.byaddr`, `ipnodes.byname`, and `ipnodes.byaddr`.

Security/reliability notes: reentrant APIs avoid static result buffers, but non-reentrant wrappers use shared static state. DNS parsing includes manual packet traversal and buffer packing; it has many bounds checks, but the alias/address accumulation paths are subtle and should be fuzzed with malformed DNS and hosts-file entries.
