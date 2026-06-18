# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/wav.c

## Role

This file parses RIFF/WAVE headers, basic audio properties, INFO metadata chunks, and optionally appended ID3v2 tags.

## Main Interface

`tagwav(Tagctx *ctx)` is the WAV parser called by `tagsget()`.

## Parsing Flow

The parser validates `RIFF` and `WAVE`, then iterates chunks. On the first `fmt ` chunk, it reads the PCM format header and sets:

- `ctx->channels`
- `ctx->samplerate`
- `ctx->duration`, estimated from remaining RIFF size and byte rate.

For `LIST` chunks it enters the list payload, and when inside `INFO`, it maps four-byte INFO keys:

- `IART`: artist.
- `ICRD`: date.
- `IGNR`: genre.
- `INAM`: title.
- `IPRD`: album.
- `ITRK`: track.
- `ICMT`: comment.
- fallback unknown key.

Values that fit in `ctx->buf` are read and emitted with `txtcb()`.

After RIFF parsing, it checks for an appended `id3 ` chunk and calls `tagid3v2()` when present.

## Risks

The parser has a simple chunk traversal model. It does not deeply handle all RIFF alignment/padding variants, but it validates chunk sizes against remaining RIFF size and skips unknown chunks.
