# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writerawimage.c

## Purpose
Writes `Rawimage` data in Plan 9 compressed image format.

## Behavior
Maps internal `Rawimage` descriptors to Plan 9 channel descriptors, writes a `compressed` header with channel string and rectangle, and compresses scanline bands using the Plan 9 image compression scheme.

## Compression
Uses hash chains over previous byte sequences, dump blocks for literals, run blocks for repeated matches, and block-size limits from draw’s compression helpers. It emits per-band headers containing ending y coordinate and compressed byte count.

## Supported Inputs
Supports `CY`, `CYA16`, `CRGBV`, `CRGBVA16`, `CRGB24`, and `CRGBA32`.
