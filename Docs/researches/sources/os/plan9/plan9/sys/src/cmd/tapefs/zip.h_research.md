# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/zip.h

This header defines ZIP constants and the parsed `ZipHead` structure used by `zipfs.c`.

Key contents:
- Magic numbers for local headers, central directory headers, and end-of-central-directory.
- General-purpose flag bits, compression method constants, CRC polynomial, and header size constants.
- Creator OS and external attribute constants.
- `ZipHead` fields for creator/extractor versions, flags, method, timestamps, CRC, compressed/uncompressed sizes, attributes, local-header offset, and filename.

Important details:
- The constants cover deflate, data descriptors, encryption flags, and OS-specific attributes, though `zipfs.c` supports only stored and deflated file data.

Filesystem relevance:
- Direct support header for the ZIP tapefs backend.
