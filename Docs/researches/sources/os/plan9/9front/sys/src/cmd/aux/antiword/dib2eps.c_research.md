# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/dib2eps.c

Converts embedded DIB bitmap images from Word streams into EPS-compatible encoded image data.

Important behavior:
- Decoders handle 1bpp, 4bpp, 8bpp, and 24bpp uncompressed DIBs.
- RLE4 and RLE8 compressed DIBs are decoded, including literal packets and end-of-line/end-of-file escapes; delta escapes terminate decoding.
- Reads DIB data through Antiword data-stream helpers (`iNextByte`, `tSkipBytes`, `ulNextLong`).
- Skips bitmap info header and color table before pixel decoding.
- Pixel output goes through `vASCII85EncodeByte()`, with 24bpp converted from BGR to RGB.
- `bTranslateDIB()` positions the data stream, emits image prologue, decodes, emits epilogue, and returns conversion success.

Filesystem relevance:
- Consumes image payloads stored in document data blocks and writes transformed output stream data.
