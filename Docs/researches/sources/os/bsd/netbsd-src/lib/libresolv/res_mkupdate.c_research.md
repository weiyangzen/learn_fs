# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_mkupdate.c

Read completely: 1169 lines.

Builds DNS UPDATE packets from linked `ns_updrec` records. `res_nmkupdate()` initializes a DNS header with update opcode, enforces section ordering beginning with the zone section, applies dynamic-update class/type overloading for prerequisites and updates, compresses owner names, and serializes RR-specific RDATA.

The large RDATA switch supports A, AAAA, CNAME/NS/PTR/DNAME-style names, SOA/MINFO/RP, MX/AFSDB/RT, SRV, PX, WKS, HINFO/TXT/X25/ISDN, NSAP, LOC, SIG, KEY, NXT, CERT, and NAPTR. Helper parsers read whitespace-delimited words, quoted strings with decimal escapes, decimal numbers, and hex numbers from in-memory text buffers.

It also provides `res_mkupdrec()`/`res_freeupdrec()` allocation helpers and cached service/protocol name-number conversion lists. Risks are typical of legacy text-to-wire parsers: many fixed buffers, partial overflow signaling via return codes, and static service/protocol caches without synchronization.
