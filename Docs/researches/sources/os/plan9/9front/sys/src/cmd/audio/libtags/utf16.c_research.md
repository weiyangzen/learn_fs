# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/utf16.c

## Role

This file converts UTF-16 metadata strings to UTF-8 for ID3v2 and related parsers.

## Main Interface

`utf16to8(uchar *o, int osz, const uchar *s, int sz)` converts up to `sz` input bytes and NUL-terminates output. It returns bytes consumed or `-1` on malformed surrogate pairs.

## Implementation Notes

The converter defaults to big-endian unless a BOM is present:

- `FE FF`: big-endian, skipped.
- `FF FE`: little-endian, skipped.

It decodes 16-bit code units, validates surrogate pairs, forms code points up to four-byte UTF-8, computes output width, and writes UTF-8 manually using the `mark[]` prefix table.

## Risks

The function assumes at least two input bytes when checking a BOM. In-tree callers use it with frame payloads large enough for text encoding markers. It stops before output overflow and leaves a valid NUL-terminated string.
