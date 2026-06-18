# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/inflate.guts.c

## Purpose
Shared gzip wrapper around Plan 9 flate decompression, included by both `expand.c` and `inflate.c` under different headers.

## Main Interfaces
- Defines `gunzip(uchar *out, int outn, uchar *in, int inn)`.

## Implementation Notes
- Defines a minimal `Biobuf` with base/current/end pointers.
- Builds a CRC table, initializes flate, parses gzip header, inflates through `inflate`, and verifies trailer CRC and uncompressed length.
- `header` handles gzip flags: extra field, original name, comment, and header CRC.
- `crcwrite` updates CRC and copies as much as fits in the output buffer, but advances the output pointer by the full decompressed count.
- `getc` returns `-1` on input exhaustion and prints `EOF`.

## Dependencies And Risks
- Uses Plan 9 `<flate.h>` APIs `inflateinit`, `inflate`, `mkcrctab`, `blockcrc`, and `flateerr`.
- `crcwrite` can report decompressed length beyond output capacity, making callers responsible for interpreting short buffers carefully.
