# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/mb_hexdump.c

Hex dumper for `mb_t` packet chains.

Key behavior:
- Walks each mbuf-like segment.
- Prints bytes as two-byte hex groups separated by spaces.
- Ends output with a newline.

Research notes:
- Similar logic is duplicated in `printpacket.c` for `OPT_HEX`.
