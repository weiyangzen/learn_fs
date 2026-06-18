# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2eps.c

PNG-to-EPS/PDF data bridge that extracts PNG IDAT chunks and forwards compressed image bytes through ASCII85 output.

Key responsibilities:
- Skips the PNG signature and walks PNG chunks until `IDAT` or `IEND`.
- Validates chunk names as alphabetic four-byte identifiers.
- Returns IDAT data lengths and skips non-image chunks plus CRCs.
- For each IDAT chunk, streams compressed data through `vASCII85EncodeArray()`.
- Wraps image data with backend image prologue/epilogue calls.
- Includes a debug-only helper to dump original PNG images to `/tmp/pic`.

Dependencies:
- Uses byte-reading helpers, PNG chunk constants, ASCII85 encoder, and backend image functions.

Notable risks:
- It does not decode PNG; it relies on downstream PostScript/PDF filters understanding the compressed IDAT stream.
- Chunk walking is minimal and treats malformed chunk names or lengths as failure.
