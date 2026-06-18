# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shcgen.h

Public interface for Huffman generation and table-construction utilities.

Key contents:
- Declares `hc_compute` for deriving a bounded canonical code from frequencies.
- Declares byte-string compression/expansion helpers for Huffman definitions.
- Declares encoding table and decoding table creation helpers.

Notable dependencies:
- Requires `shc.h` types such as `hc_definition`, `hce_code`, and `hcd_code`.
- Uses `gs_memory_t` for allocation in `hc_compute`.

Research notes:
- This header is consumed by filters that need dynamic Huffman tables rather than fixed tables.
