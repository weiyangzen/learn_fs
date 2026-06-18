# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/m4a.c

## Role

This file parses M4A/QuickTime-style atoms for audio metadata, stream parameters, duration, track number, genre, and cover art.

## Main Interface

`tagm4a(Tagctx *ctx)` is the M4A parser called by `tagsget()`.

## Container Traversal

The parser expects an `ftypM4A ` atom at the start. It then walks atoms by size and type. For container atoms such as `udta`, `ilst`, `trak`, `mdia`, `minf`, `moov`, and `stbl`, it descends by resetting the skip size to zero. For `meta`, it skips the four metadata flags/version bytes.

## Metadata Atoms

It maps common atoms to tag types:

- `©nam`: title.
- `©alb`: album.
- `©ART`: artist.
- `aART`: album artist.
- `©gen` and `gnre`: genre.
- `©day`: date.
- `covr`: image.
- `trkn`: track.
- `©wrt`: composer.
- `©cmt`: comment.

Text payloads with data type `1` are read into `ctx->buf` and emitted directly. Numeric genres are mapped through `id3genres`. JPEG and PNG covers are reported as `Timage` with file offset and size.

## Stream Metadata

For `stsd` sample descriptions, the parser reads `mp4a` entries and sets `ctx->channels` and `ctx->samplerate`.

For `mdhd`, it handles version 0 and a version-1-like path, reading timescale and duration fields and setting `ctx->duration` in milliseconds.

## Risks

The atom walker is simple and assumes atom sizes are sane. Some unsupported atoms are skipped silently. Large text atoms that do not fit in `ctx->buf` are skipped.
