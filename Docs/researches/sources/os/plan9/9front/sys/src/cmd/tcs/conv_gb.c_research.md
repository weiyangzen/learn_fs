# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_gb.c

Implements GB2312 decoding and encoding around the `tabgb` mapping table.

Key points:
- `gbproc` is a two-state parser: bytes below `0xA1` are emitted directly; bytes `>= 0xA1` begin a two-byte GB sequence.
- Valid pairs are converted to a kuten-like ordinal with `(lead - 0xA0) * 100 + (trail - 0xA0)`.
- Unknown or invalid pairs increment `nerrors`, optionally warn with byte offsets and source filename, and emit `BADMAP` unless `clean` is set.
- `gb_in` streams input through `gbproc`, flushes full output buffers via `OUT`, handles EOF, and emits a final zero-length downstream marker.
- `gb_out` lazily builds the shared reverse table from `tabgb`, emits ASCII directly, and encodes mapped Runes as two bytes using the stored ordinal.
- Unmappable Runes warn under `squawk`, increment `nerrors`, and emit `BYTEBADMAP` unless clean output is requested.

Dependencies and interactions:
- Includes `gb.h` for `GBMAX` and `tabgb`.
- `tcs.c` registers this as the functional converter for `gb2312`.

Research relevance:
- Main runtime bridge between GB2312 bytes and Unicode Runes.
