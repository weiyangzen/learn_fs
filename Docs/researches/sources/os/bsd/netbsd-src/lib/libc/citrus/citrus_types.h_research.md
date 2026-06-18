# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_types.h

Read completely: 41 lines.

This header defines Citrus scalar types: `_citrus_wc_t`, `_citrus_index_t`, and `_citrus_csid_t` as `uint32_t`, plus `_CITRUS_CSID_INVALID` as all-ones.

These types are the common representation for wide-character values, mapping indices, and character-set IDs across stdenc, mapper, and iconv modules.

Security/reliability notes: no executable logic. The fixed 32-bit width is central to file-format and ABI compatibility.
