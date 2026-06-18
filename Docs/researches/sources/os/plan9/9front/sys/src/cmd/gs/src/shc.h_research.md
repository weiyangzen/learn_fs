# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/shc.h

Defines common data structures and macros for Huffman-coded filters.

Key points:
- Defines canonical Huffman `hc_definition` tables using per-length counts and lexicographically ordered decoded values.
- Defines `stream_hc_state_common` with `FirstBitLowOrder`, bit buffer, and bit count.
- Defines encode-side tables `hce_code`/`hce_table` and macros for loading/storing state and emitting codes.
- Defines decode-side tables `hcd_code`/`hcd_table` and explains first-level versus second-level dispatch table layout.
- Provides macros for checking/ensuring bits, loading more bits with optional bit reversal, peeking fixed or variable bit counts, and skipping bits.
- Supports code lengths up to 16 bits and non-negative decoded values up to 15 bits.

Dependencies and interactions:
- Used by stream filters that share Huffman bit-buffer mechanics.
- `shc.c` supplies the non-macro helper routines for flushing code words and final bits.

Research relevance:
- This header is the reusable Huffman bit I/O and table format layer.
