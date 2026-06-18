# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_send.c

Read completely: 1225 lines.

This file implements resolver transport: `res_nsend`, `res_ourserver_p`, `res_nameinquery`, and `res_queriesmatch`, plus TCP (`send_vc`) and UDP (`send_dg`) helpers.

Key behavior: `res_nsend` reloads resolver config via `res_check`, validates server/socket caches, optionally rotates nameservers, applies query/response hooks, chooses TCP for `RES_USEVC` or oversized packets, retries across servers/attempts, and prints debug packets. UDP sockets may be connected for ICMP error feedback unless `RES_INSECURE1` is set. Responses are checked for matching ID, expected server, matching query section unless `RES_INSECURE2`, EDNS FORMERR fallback, SERVFAIL/NOTIMP/REFUSED retry policy, and TC fallback to TCP. TCP sends a two-byte length prefix and drains truncated responses to keep stream sync.

Important interactions: called by `res_query.c`; uses `res_private.h` server extension, `res_debug.h` diagnostics, nameser compression/parsing helpers, and libc socket/event APIs.

Security/reliability notes: spoof resistance depends on ID, source-server, and query-section checks, which resolver options can weaken. The UDP path contains a suspicious conditional typo in the `SOCK_CLOEXEC == 0` branch (`EXT(statp)nssocks[ns]`) that would matter on platforms lacking `SOCK_CLOEXEC`. Manual timeout/retry logic and stream resynchronization are critical test areas.
