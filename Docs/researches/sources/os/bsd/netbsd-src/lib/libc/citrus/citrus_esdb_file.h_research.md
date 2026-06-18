# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb_file.h

Symbol definitions for ESDB compiled database files.

Key contents:
- Magic: `ESDB\0\0\0\0`.
- Symbol names for version, encoding, variable, number of charsets, invalid character, charset name prefix, and charset id prefix.
- Current version constant `0x00000001`.

These constants must match ESDB compiler output and `citrus_esdb.c` lookup keys.
