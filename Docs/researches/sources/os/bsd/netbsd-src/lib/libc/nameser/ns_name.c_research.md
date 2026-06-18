# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_name.c

Read completely: 1153 lines.

This file implements DNS counted-name conversion, compression, decompression, comparison, and label mapping helpers for libc/resolver. Public entry points include `ns_name_ntop`, `ns_name_pton`, `ns_name_pton2`, `ns_name_ntol`, `ns_name_unpack`, `ns_name_unpack2`, `ns_name_pack`, `ns_name_uncompress`, `ns_name_compress`, `ns_name_rollback`, `ns_name_skip`, `ns_name_length`, `ns_name_eq`, `ns_name_owned`, `ns_name_map`, and `ns_name_labels`.

Key behavior: presentation names are escaped per RFC1035, wire-format names enforce label and total-name limits, unpacking follows DNS compression pointers with loop detection via a checked-byte counter, packing searches `dnptrs` for reusable suffixes, and comparison/mapping routines reject compressed names for uncompressed counted-name operations. The file also preserves legacy EDNS0 bitstring label support through `DNS_LABELTYPE_BITSTRING`, with `encode_bitsring`, `decode_bitstring`, and `labellen`.

Important interactions: `ns_parse.c`, `ns_print.c`, `getaddrinfo.c`, and `gethnamaddr.c` depend on these routines through resolver/name macros such as `dn_expand`, `dn_skipname`, and direct `ns_name_unpack2`. Compression pointer state is caller-owned via `dnptrs`, so rollback support matters when message construction fails.

Security/reliability notes: most paths set `errno` to `EMSGSIZE`, `EINVAL`, `ENOENT`, or `EISDIR` on malformed input. The code carefully bounds destination writes and source reads, but it assumes callers pass a valid DNS message span. Bitstring-label support is obsolete and more intricate than ordinary labels, so changes near `encode_bitsring`/`decode_bitstring` need dedicated malformed-input tests.
