# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/zip.h

`zip.h` defines ZIP constants and the `ZipHead` metadata structure for `zipfs.c`.

Contents:
- Local, central, and end-central-directory magic numbers.
- General-purpose flags such as encryption, data trailer, and patched compression.
- Compression method constant for deflate.
- CRC polynomial.
- Internal/external attribute constants and creator OS ids.
- Header size constants for local, trailer, central, and end-central records.

`ZipHead` fields:
- Creator/extractor OS and version.
- Flags, method, DOS mod time/date.
- CRC, compressed size, uncompressed size.
- Internal/external attributes.
- Local header offset.
- Allocated file name.

Use:
- `zipfs.c` fills `ZipHead` from central and local headers, then uses it to populate `Fileinf` and drive reads/decompression.

Risks:
- ZIP64 is not represented.
- Only legacy 32-bit size/offset fields are modeled.
