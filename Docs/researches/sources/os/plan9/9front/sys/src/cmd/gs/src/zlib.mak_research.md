# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zlib.mak

## Purpose
Partial makefile for compiling or linking zlib as part of Ghostscript.

## Key Targets
- `zlibc.dev` builds common zlib support from `zutil`.
- `zlibe.dev` selects shared or compiled encode/compression support.
- `zlibd.dev` selects shared or compiled decode/decompression support.
- `crc32.dev` handles crc32 as its own module because libpng needs it.

## Important Behavior
- Controlled by `SHARE_ZLIB`: `1` links against `ZLIB_NAME`, `0` compiles bundled zlib sources.
- Documents expected zlib source version 1.2.1 and warns about older zlib issues.
- Uses generated `.dev` module descriptions with `SETMOD` and `ADDMOD`.
- Compiles `crc32.c` with warnings disabled because of 32-bit constants under `-Wtraditional`.

## Research Notes
Build-system integration only; no runtime interpreter code.
