# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/dib2sprt.c

RISC OS-specific DIB-to-sprite converter for Antiword.

Important behavior:
- Computes sprite row byte widths for 1, 4, 8, and 24 bpp images.
- `pCreateBlankSprite()` allocates a RISC OS sprite area, chooses screen mode, creates a blank sprite, and installs palettes for indexed images.
- Converts 24-bit color into RISC OS default 256-color palette via `iReduceColor()`.
- Decoders handle uncompressed 1/4/8/24 bpp DIBs and RLE4/RLE8 compressed DIBs, writing rows bottom-up into sprite memory.
- `vDecodeDIB()` skips DIB headers/color tables, creates a sprite, decodes pixels, embeds the sprite into the Draw diagram, then frees memory.
- `bTranslateDIB()` positions the Antiword data stream and invokes decoding.

Filesystem relevance:
- Translates binary document image stream data into RISC OS sprite objects for Draw output.
