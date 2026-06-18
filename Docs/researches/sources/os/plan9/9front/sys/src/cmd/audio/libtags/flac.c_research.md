# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/flac.c

## Role

This file extracts basic stream information, Vorbis comments, and embedded pictures from FLAC files.

## Main Interface

`tagflac(Tagctx *ctx)` is the FLAC parser called by `tagsget()`.

## Parsing Flow

The parser expects the FLAC marker and first metadata block at the beginning of the stream. It reads the STREAMINFO block, sets:

- `ctx->samplerate`
- `ctx->channels`
- `ctx->duration`

It then iterates FLAC metadata blocks until the last-block flag is seen.

For block type `6` PICTURE, it reads image type, MIME length, description length, image metadata, and image data size, then calls `tagscallcb()` with `Timage`, MIME type, file offset, and image size.

For block type `4` VORBIS_COMMENT, it skips the vendor string, reads the comment count, reads each `key=value` entry that fits in `ctx->buf`, trims a trailing carriage return, and dispatches through `cbvorbiscomment()`.

Other metadata blocks are skipped.

## Dependencies

The file uses endian helpers from `tagspriv.h`, the shared Vorbis comment mapper in `vorbis.c`, and the callback helpers from `tags.c`.

## Risks

The parser is intentionally small and mostly linear. It validates sizes against remaining block length and buffer size, but malformed metadata can still cause an early `-1` rather than partial recovery.
