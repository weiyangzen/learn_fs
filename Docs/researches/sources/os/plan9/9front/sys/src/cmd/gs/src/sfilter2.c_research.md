# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sfilter2.c

Implements simple Level 2 filters: `ASCII85Encode` and byte-translate encode/decode.

Key points:
- `s_A85E_process` encodes 4-byte groups to ASCII85, emits `z` for zero words, wraps at 79 characters, and writes the final `~>` marker on last input.
- Includes compatibility logic to avoid output lines beginning with `%%` or `%!`, which can confuse document managers.
- Handles partial final words by padding internally and emitting the correct shortened ASCII85 character count.
- Maintains line position and previous character in the stream state.
- `s_BT_process` applies a 256-byte translation table byte-for-byte and is shared by `ByteTranslateEncode` and `ByteTranslateDecode`.

Dependencies and interactions:
- Uses ASCII85 and byte-translate state declarations from `sa85x.h` and `sbtx.h`.
- Uses Ghostscript debug channel `w` for optional tracing.

Research relevance:
- Supplies ASCII armor and simple byte remapping filters used in PostScript/PDF stream pipelines.
