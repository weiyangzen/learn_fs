# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_debug.c

Read completely: 1250 lines.

This file implements resolver/DNS debugging and presentation helpers: `res_pquery`, compressed-name printers, DNS class/type/rcode/section symbol tables, option/time/address string helpers, DNS LOC RDATA conversion, label counting, DNSSEC time formatting, and `res_nametoclass`/`res_nametotype`.

Key behavior: `res_pquery` parses a DNS packet with `ns_initparse`, prints header flags/counts, and delegates each section to `do_section`. `do_section` uses `ns_parserr`/`ns_sprintrr`, with special handling for EDNS OPT records and NSID display. Symbol helpers translate numeric DNS values to mnemonics and fallback `TYPE####`/`CLASS####` forms. `loc_aton` and `loc_ntoa1` convert DNS LOC records between zone-file text and 16-byte wire format.

Important interactions: used by resolver debug paths in `res_send.c`, query wrappers in `res_data.c`, DNS RR printers in `ns_print.c`, and callers expecting legacy BIND resolver symbols such as `p_type`, `p_class`, `p_rcode`, `p_time`, and `p_secstodate`.

Security/reliability notes: many formatters return pointers to static buffers and are not reentrant. The EDNS option printing loop resets its RDATA cursor each iteration and does not check `optlen` against remaining RDATA before reading option bytes, making malformed OPT records a sensitive area. `p_sockun` writes `'0'` instead of `'\0'` as the destination terminator, which looks like a bug.
