# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v1.c

## Role

This file parses ID3v1 tags from the last 128 bytes of MP3 files.

## Main Interface

`tagid3v1(Tagctx *ctx)` seeks to `-128` from EOF, verifies the `TAG` marker, and extracts title, artist, album, date, comment, track, and genre.

## Parsing Details

It requires `ctx->bufsz >= 189` so the 128-byte input and a 61-byte conversion output can coexist in `ctx->buf`.

Fields are decoded as ISO-8859-1:

- Title: bytes 3-32.
- Artist: bytes 33-62.
- Album: bytes 63-92.
- Date: bytes 93-96.
- Comment: starts at byte 97.
- Track: ID3v1.1 layout when byte 125 is zero and byte 126 is nonzero.
- Genre: byte 127, mapped through `id3genres`.

The parser respects tags already found by ID3v2 by checking `ctx->found` before emitting overlapping fields.

## Risks

The comment field handling is minimal and depends on NUL placement in the buffer. The parser is deliberately tolerant because ID3v1 data is often loosely formatted.
