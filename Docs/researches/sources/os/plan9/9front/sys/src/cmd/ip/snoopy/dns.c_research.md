# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dns.c

This module decodes DNS messages using 9front’s NDB DNS parser structures from `../../ndb/dns.h`. It prints the DNS header first, then exposes synthetic sequential protocols for question, answer, authority, and additional records.

`p_seprint` calls `convM2DNS`; on success it prints id and flags and sets `m->pr` to the first non-empty section. The section printers `p_seprintqd`, `p_seprintan`, `p_seprintns`, and `p_seprintar` each print one RR via `fmtrr`, advance the linked list, and select the next section or clean up.

`fmtrr` handles many RR types: A, AAAA, NS, CNAME, SOA, MX, PTR, TXT, NULL, RP, KEY, SIG, CERT, CAA, OPT, and unknown data. It frees each RR after printing.

The bottom portion is copied support logic from `/sys/src/cmd/ndb/dn.c`, including RR type name lookup, allocation, and freeing. Local `dnlookup`, `emalloc`, `estrdup`, and `dnslog` stubs support parsing without normal resolver database behavior.
