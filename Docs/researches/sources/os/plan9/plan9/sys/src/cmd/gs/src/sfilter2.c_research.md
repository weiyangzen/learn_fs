# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfilter2.c

Simple Level 2 stream filters: ASCII85 encode and byte-translation encode/decode.

Key behavior:
- `ASCII85Encode` initializes inline state, emits 4-byte groups as 5 ASCII85 bytes, uses `z` for all-zero words, emits `~>` on final data, and wraps output at 79 columns.
- It contains compatibility guards to avoid producing line starts that confuse document managers, specifically `%!` or `%%`.
- Final partial words are padded internally and emitted with the required shortened ASCII85 output.
- `ByteTranslateEncode` and `ByteTranslateDecode` share `s_BT_process`, mapping every input byte through a 256-entry translation table.

Notable dependencies:
- ASCII85 state from `sa85x.h`.
- Byte-translate state from `sbtx.h`.
- Debug tracing through `gdebug.h`.

Research notes:
- The ASCII85 loop is careful about buffer limits and line wrapping; status `1` indicates output buffer exhaustion.
- ByteTranslate is deliberately symmetric: encode and decode differ only by the caller-supplied table.
