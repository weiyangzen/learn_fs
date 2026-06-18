# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/vorbis.c

## Role

This file parses Vorbis comments from Ogg Vorbis files, maps Vorbis comment keys to libtags tag types, extracts basic stream parameters, and estimates duration.

## Shared Comment Mapping

`cbvorbiscomment(Tagctx *ctx, char *k, char *v)` maps case-insensitive keys such as `album`, `title`, `artist`, `tracknumber`, `date`, ReplayGain/R128 keys, `genre`, `composer`, `comment`, `albumartist`, and `album artist`.

Unknown non-empty keys are emitted as `Tunknown`.

This mapper is also used by FLAC and Opus parsers.

## Vorbis Parsing

`tagvorbis(Tagctx *ctx)` manually reads the first Ogg pages. It looks for:

- Identification packet (`type == 1`): reads channels, sample rate, and bitrate fields.
- Comment packet (`type == 3`): records packet end and breaks to comment parsing.

It validates the `"vorbis"` marker in the comment header, skips the vendor string, reads the number of tags, and parses `key=value` comment entries that fit in `ctx->buf`.

## Duration

If sample rate is known, it scans around the current position to find an initial Ogg page granule position, then scans backward near EOF for the last page with EOS set. Duration is `(last_granule - first_granule) * 1000 / samplerate`.

## Risks

The parser is deliberately lightweight and does not use libogg's full sync/page parser. FIXME comments note that embedded pictures can make tags span multiple packets; such oversized/multipacket comments are not fully supported.
