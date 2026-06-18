# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/Makefile.inc

Read completely: 13 lines.

This makefile fragment adds DNS nameserver helper sources: `ns_name.c`, `ns_netint.c`, `ns_parse.c`, `ns_print.c`, `ns_samedomain.c`, and `ns_ttl.c`.

Important interactions: sets `.PATH` to `${.CURDIR}/nameser` and applies a lint suppression to `ns_name.c` for a table initialized with `-1` in `char` storage.

Security/reliability notes: no runtime behavior in this fragment. The lint note documents intentional unsigned char conversion behavior in DNS name parsing tables.
