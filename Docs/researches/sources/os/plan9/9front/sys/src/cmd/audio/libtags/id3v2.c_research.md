# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/id3v2.c

## Role

This file parses ID3v2 tags and derives MP3 stream duration/TOC metadata when possible.

## Main Interface

`tagid3v2(Tagctx *ctx)` is the ID3v2/MP3 parser called by `tagsget()`.

## Tag Mapping

`v2cb()` maps ID3 frame keys to libtags tag types. It recognizes album, artist, album artist, title, date/year, track, length, composer, genre, comment, and ReplayGain-style `TXXX` frames. Unknown text frames are emitted as `Tunknown`.

Genre parsing handles numeric parenthesized genre values by indexing `id3genres`, while also accepting plain-text genres.

## Text and Binary Frames

`text()` reads a text frame into the end of `ctx->buf`, applies unsynchronization removal when needed, decodes by encoding byte, and dispatches through `v2cb()`:

- `0`: ISO-8859-1.
- `1` and `2`: UTF-16.
- `3`: UTF-8.

`nontext()` handles:

- `APIC`: ID3v2 attached picture, reporting MIME type, image offset, size, and optional unsync read filter.
- `PIC`: ID3v2.2 picture frame, mapping `JPG` to JPEG and otherwise using PNG.
- `RVA2`: replay gain data via `rva2()`.

`resync()` and `unsyncread()` remove ID3 unsynchronization byte stuffing.

## Header and Frame Parsing

`isid3()` validates the ID3 header and synchsafe size bytes. `tagid3v2()` supports v2.2, v2.3, and v2.4 frame layouts:

- Handles global unsynchronization.
- Rejects unsupported v2.2 compression.
- Skips v2.3/v2.4 extended headers.
- Accounts for v2.4 footers.
- Skips compressed/encrypted frames.
- Skips v2.4 data length indicators.
- Stops on padding.

After one tag is parsed, it scans ahead up to 2048 bytes for chained ID3 headers and MP3 frame sync.

## MP3 Duration and TOC

`getduration()` reads an MPEG audio header, sets bitrate, sample rate, and channel count from static lookup tables, and estimates duration. It recognizes Xing/Info and VBRI headers. If a Xing TOC is present and `ctx->toc` is configured, it emits approximate millisecond-to-byte offsets.

As fallback, it estimates duration from file size and bitrate.

## Risks

ID3v2 is highly variable. This parser is defensive and compact, but not exhaustive. It ignores frames that do not fit in the working buffer, skips unsupported compression/encryption, and has FIXME notes around image unsync streaming and UTF-8 boundary handling in lower-level converters.
