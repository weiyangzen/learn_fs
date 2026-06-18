# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/asc85enc.c

ASCII85 encoder used by Antiword image/output paths, especially PostScript/PDF image embedding.

Important behavior:
- `vASCII85EncodeByte()` buffers four input bytes, emits five ASCII85 characters, uses `z` shortcut for zero blocks, and emits `~>\n` at EOF.
- Handles partial final groups correctly.
- `vOutputByte()` limits output lines to 64 characters and avoids two `%` characters at the start of a line by forcing a line break.
- `vASCII85EncodeArray()` reads bytes through `iNextByte()` from the Antiword data stream.
- `vASCII85EncodeFile()` encodes a bounded byte count and finalizes the stream.

Filesystem relevance:
- Converts binary image payloads read from Word/OLE streams into text-safe output file encoding.
