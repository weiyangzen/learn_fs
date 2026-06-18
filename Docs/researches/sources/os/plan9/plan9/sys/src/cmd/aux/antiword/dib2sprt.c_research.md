# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/dib2sprt.c

This RISC OS-specific file translates embedded DIB images into RISC OS sprite objects for Draw output.

Key behavior:
- Computes sprite row byte widths for 1, 4, 8, and 24 bpp images.
- Allocates and initializes a sprite area, including palettes for low-color images.
- Reduces 24-bit and palette colors to the RISC OS default 256-color palette.
- Decodes uncompressed and RLE4/RLE8 DIB data into sprite pixel memory.
- Reverses bit/nibble ordering and writes rows bottom-up.
- Wraps the sprite into the current Draw diagram through `vImage2Diagram()`.

Important details:
- Uses DeskLib Sprite APIs and is not part of the Plan 9 build path.
- Reads image bytes through the Antiword data-list cursor.
- Debug sprite dumping is present but disabled by `#if 0`.

Filesystem relevance:
- Indirect: converts image data extracted from document storage; platform-specific rendering code.
