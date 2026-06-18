# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/slzwx.h

Defines LZW filter state and templates.

Key points:
- Declares decode and encode table opaque types.
- `stream_LZW_state` includes decode parameters (`InitialCodeLength`, `FirstBitLowOrder`, `BlockData`, `EarlyChange`) and dynamic bit/table/code/copy state shared by encoder and decoder.
- Defaults set PostScript/PDF-style initial code length 8, high-bit-first ordering, no block data, and `EarlyChange = 1`.
- Declares `s_LZWD_template`, `s_LZWE_template`, and shared default/release procedures.

Research relevance:
- Central state contract for Ghostscript LZW compression and decompression.
