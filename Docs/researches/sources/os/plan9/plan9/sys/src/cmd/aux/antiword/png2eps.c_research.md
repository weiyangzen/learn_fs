# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2eps.c

## Summary
`png2eps.c` translates PNG image payloads from a Word document into backend image output by streaming PNG `IDAT` chunks through ASCII85 encoding.

## Main Responsibilities
- Validates and skips the PNG signature.
- Walks PNG chunks, searching for `IDAT` data and stopping at `IEND`.
- Skips chunk payloads and CRCs while tracking remaining byte budget.
- Emits backend image prologue/epilogue calls.
- Sends compressed IDAT bytes unchanged through `vASCII85EncodeArray()`, relying on PS/PDF Flate decode filters.
- In debug builds, can dump extracted PNG bytes to `/tmp/pic/picNNNN.png`.

## Key Dependencies
Uses PNG chunk constants from `antiword.h`, file-position helpers such as `bSetDataOffset()`, byte readers, ASCII85 encoders, and backend image functions.

## Filesystem Relevance
Reads image bytes from the Word document stream. Debug dumping writes temporary PNG files.

## Notes
This is not a full PNG decoder; it preserves compressed pixel data and lets the output backend declare the decompression/filter pipeline.
