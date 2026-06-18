# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_query.c

Read completely: 473 lines.

This file implements high-level DNS querying and search behavior: `res_nquery`, `res_nsearch`, `res_nquerydomain`, and `res_hostalias`.

Key behavior: `res_nquery` builds a packet with `res_nmkquery`, appends EDNS0/NSID options when configured, sends with `res_nsend`, maps DNS rcodes and empty-answer cases to `h_errno`, and retries without EDNS0 after detected EDNS failures. `res_nsearch` implements `ndots`, trailing-dot, `RES_DEFNAMES`, `RES_DNSRCH`, `RES_NOTLDQUERY`, and search-list behavior. `res_nquerydomain` concatenates name/domain or strips a final root dot. `res_hostalias` reads `HOSTALIASES` unless disabled or running setuid/setgid.

Important interactions: this is the main query API under libc resolver wrappers; it depends on `res_mkquery.c`, `res_send.c`, nameser comparison helpers, and resolver state from `res_init.c`.

Security/reliability notes: `res_hostalias` explicitly rejects aliases for `issetugid()` programs. DNS search behavior intentionally continues after `NO_DATA` and selected `SERVFAIL` cases, which is compatibility-sensitive.
