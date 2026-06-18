# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gbk.c

Implements GBK decoding and encoding around the `tabgbk` mapping table.

Key points:
- `gbkproc` treats bytes below `0x80` as direct output and bytes `>= 0x80` as the first byte of a two-byte GBK sequence.
- Combines a byte pair into `lead << 8 | trail`, checks it against `GBKMIN <= code < GBKMAX`, and indexes `tabgbk[code - GBKMIN]`.
- Invalid or unmapped pairs increment `nerrors`, optionally warn, and emit `BADMAP` unless `clean` is set.
- `gbk_in` uses the same buffered streaming pattern as the other multibyte decoders.
- `gbk_out` lazily populates the shared reverse table from `tabgbk`, emits bytes below `0x80` directly, and writes mapped Runes as two GBK bytes.

Dependencies and interactions:
- Includes `gbk.h` for `GBKMIN`, `GBKMAX`, and `tabgbk`.
- Registered by `tcs.c` as the `gbk` converter.

Research relevance:
- Runtime implementation for GBK, including byte-range validation and reverse mapping.
