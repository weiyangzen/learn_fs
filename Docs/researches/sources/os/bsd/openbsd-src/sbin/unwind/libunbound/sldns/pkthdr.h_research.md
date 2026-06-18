# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/pkthdr.h

`pkthdr.h` defines DNS packet header constants, flag masks, and accessor macros for raw wire buffers. It covers the 12-byte DNS header, query ID, section counts, and all standard first/second flag-octet bits: QR, opcode, AA, TC, RD, RA, Z, AD, CD, and RCODE.

The macros read and update raw header bytes in place, using `sldns_read_uint16()` and `sldns_write_uint16()` for multi-byte fields. They assume the caller has a valid DNS header buffer.

The header also defines enums for packet sections, opcodes, and base RCODEs. It contains no functions; it is a low-level wire-buffer convenience layer used by packet parsing, construction, and mutation code.
