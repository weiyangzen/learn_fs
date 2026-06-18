# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.h

## Role

This is the public libtags API header for 9front audio metadata parsing. It declares tag types, format identifiers, `Tagctx`, and `tagsget()`.

It includes a Plan 9 `#pragma lib` for `/sys/src/cmd/audio/libtags/libtags.a$O`.

## Public Types

`Tagctx` contains caller-provided callbacks:

- `read(ctx, buf, cnt)`
- `seek(ctx, offset, whence)`
- `tag(ctx, type, key, string, image_offset, image_size, filter)`
- optional `toc(ctx, ms, offset)`

It also carries caller auxiliary data, a working buffer, output stream fields, and private parser state.

`Tagread` is a filter callback type used for binary image payloads that require transformation while reading.

## Tag Types

Known tag types include artist, album, title, date, track, album/track gain and peak, genre, image, composer, comment, and album artist. `Tunknown` is `-1`.

The gain note warns that ReplayGain/R128 values may not always be simple `dB` strings; callback consumers must inspect the raw key.

## Format Types

Format identifiers include MP3, Vorbis, FLAC, M4A, Opus, WAV, IT, XM, S3M, MOD, plus unknown.

## Integration Notes

Callers must allocate `ctx->buf` with at least 256 bytes before calling `tagsget()`. After parsing, `channels`, `samplerate`, `bitrate`, `duration`, and `format` may be populated.
