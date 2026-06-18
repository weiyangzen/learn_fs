# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writegif.c

## Purpose
GIF writer for `Image` and `Memimage`.

## API Surface
Exports `startgif`, `writegif`, `endgif`, and memimage variants.

## Format Handling
Writes GIF89a header, logical screen descriptor, global color table for GREY1/2/4/8 or CMAP8, optional Netscape loop extension, optional comment extension, optional Graphic Control Extension with delay/transparency, image descriptor, LZW image data, and trailer.

## Compression
Implements GIF LZW encoding with clear code, EOD code, dynamic dictionary, 12-bit limit, hash lookup, and sub-block output capped at 255 bytes.

## Limits
Only grey and CMAP8-style channels are accepted; callers convert richer images first.
