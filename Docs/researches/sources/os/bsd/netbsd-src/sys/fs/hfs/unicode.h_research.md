# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/unicode.h

## Purpose
Declares the HFS local Unicode conversion helpers and conversion flags.

## Main Contents
Defines `UNICODE_DECOMPOSE`, `UNICODE_PRECOMPOSE`, and `UNICODE_UTF8_LATIN1_FALLBACK`, then declares `utf8_to_utf16()` and `utf16_to_utf8()`.

## Dependencies
Includes `sys/types.h` for fixed-width and size types.

## Risks and Notes
There is no include guard in this header. Decompose/precompose flags are declared but the implementation does not perform normalization.
