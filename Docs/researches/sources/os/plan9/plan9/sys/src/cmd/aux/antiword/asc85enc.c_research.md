# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/asc85enc.c

This file implements ASCII85 encoding for image/data streams written to PostScript or PDF-like output.

Key behavior:
- Buffers groups of four input bytes and emits five ASCII85 characters.
- Uses `z` as the compact encoding for all-zero 32-bit groups.
- Flushes partial groups and writes the `~>` end marker when passed `EOF`.
- Provides helpers to encode a fixed-length byte array or file region using Antiword’s data-stream reader.
- Limits output lines and avoids starting a line with `%%`, which can confuse some PostScript post-processors.

Important details:
- Encoder state is static, so each stream must be ended with `vASCII85EncodeByte(..., EOF)` to reset state.
- `vASCII85EncodeArray()` reads via `iNextByte()`, so it depends on `datalist.c` cursor state.

Filesystem relevance:
- Indirect: transforms embedded document image bytes after they have been mapped from file storage.
