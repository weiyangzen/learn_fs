# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_big5.c

Implements Big5 decoding and encoding around the `tabbig5` mapping table.

Key points:
- `big5proc` is a two-state byte parser: ASCII/control bytes are emitted directly, while bytes `>= 0xA1` start a two-byte Big5 sequence.
- Second bytes are normalized from Big5 trail ranges `0x40-0x7E` and `0xA1-0xFE` into a `BIG5FONT` ordinal.
- Lead bytes are normalized from `0xA1-0xFE`; invalid lead/trail bytes increment `nerrors`, optionally warn, and emit `BADMAP` unless `clean` is set.
- `big5_in` streams file input in `N`-byte chunks, flushes output through `OUT`, sends EOF with `big5proc(-1, ...)`, and terminates downstream with a zero-length `OUT`.
- `big5_out` lazily builds the shared reverse table from `tabbig5`, emits ASCII directly, and writes two-byte Big5 sequences for mapped Runes.
- Unmappable output Runes warn under `squawk`, increment `nerrors`, and emit `BYTEBADMAP` unless `clean` is set.
- There is a branch for `r >= BIG5MAX` after reverse lookup, but reverse table values are built only from indices below `BIG5MAX`, so that branch appears unreachable for the local table.

Dependencies and interactions:
- Includes `big5.h` for `BIG5MAX`, `BIG5FONT`, and `tabbig5`.
- Uses globals/macros from `hdr.h` and `conv.h`: `BADMAP`, `BYTEBADMAP`, `OUT`, `obuf`, counters, `file`, `clean`, and `squawk`.

Research relevance:
- Runtime implementation for Big5 in `tcs`; tightly coupled to the generated/static Big5 table.
