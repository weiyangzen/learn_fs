# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/shcgen.c

Generates bounded Huffman definitions and encode/decode tables.

Key points:
- `hc_compute` builds a Huffman tree from value frequencies, derives code lengths, limits them to `def->num_counts`, sorts values into canonical order, and fills `hc_definition`.
- `hc_limit_code_lengths` adjusts overlong code lengths while preserving a complete prefix code under the configured maximum length.
- Provides conversion between well-behaved Huffman definitions and compact byte strings where each byte encodes a run length and code length.
- `hc_sizes_from_bytes` recovers required counts/value sizes before allocating a definition.
- `hc_definition_from_bytes` reconstructs counts and values from the compact run representation.
- `hc_make_encoding` creates canonical encoding tables.
- `hc_sizeof_decoding` and `hc_make_decoding` build one- or two-dispatch decode tables for efficient bit decoding.

Dependencies and interactions:
- Uses `shc.h` definitions and Ghostscript memory allocation.
- Debug output can print node lists and code-length distributions.

Research relevance:
- This is the table-construction engine behind reusable Huffman-coded filters.
