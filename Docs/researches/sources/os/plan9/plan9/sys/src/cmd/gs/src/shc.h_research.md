# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/shc.h

Common Huffman coding definitions, state, tables, and bit-buffer macros.

Key contents:
- Defines `hc_definition`: canonical Huffman code counts by length plus decoded values in lexicographic code order.
- Defines `stream_hc_state_common` with `FirstBitLowOrder`, `bits`, and `bits_left`.
- Defines encode table structures `hce_code` and `hce_table`.
- Provides encoder macros for loading/storing state and emitting code values into an output bit buffer.
- Defines decode table structures `hcd_code` and `hcd_table`.
- Provides decoder macros for loading/storing state, ensuring bits, reading more input bytes, peeking bits, and skipping bits.

Notable dependencies:
- `gsbittab.h` for bit reversal and masks.
- `scommon.h` stream-state common definitions.

Research notes:
- The header supports code lengths up to 16 bits and decoded values up to 15 bits.
- Decoding is designed as a two-level table lookup: fixed initial bits and optional auxiliary subtables.
- The macros depend on Ghostscript’s one-byte-before-cursor stream cursor convention.
