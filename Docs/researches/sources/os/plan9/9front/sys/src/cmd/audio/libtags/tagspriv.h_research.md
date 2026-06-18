# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tagspriv.h

## Role

This private header centralizes libtags internal dependencies, endian helpers, charset converters, shared callbacks, and parser declarations.

## Main Definitions

It includes Plan 9 headers `<u.h>` and `<libc.h>`, then the public `tags.h`.

It defines:

- `Numgenre = 192`.
- `beuint(d)` and `leuint(d)` 32-bit endian macros.
- `id3genres` external table.

## Internal Helpers

Declared helpers include:

- `iso88591toutf8()`
- `utf16to8()`
- `cp437toutf8()`
- `cbvorbiscomment()`
- `tagscallcb()`
- `txtcb()` macro for normal text callbacks.

## Parser Declarations

It declares all format parser functions used by `tags.c`: FLAC, ID3v1, ID3v2, IT, M4A, Opus, S3M, Vorbis, WAV, XM, and MOD.

## Integration Notes

This header is the internal coupling point for all libtags implementation files. Changes to `Tagctx` public fields or helper semantics affect every parser.
