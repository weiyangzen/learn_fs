# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/tags.c

## Role

This file is the dispatcher and common callback wrapper for libtags.

## Parser Dispatch

`tagsget(Tagctx *ctx)` initializes output fields and tries each parser in order:

1. ID3v2 / MP3.
2. ID3v1.
3. Vorbis.
4. FLAC.
5. M4A.
6. Opus.
7. WAV.
8. IT.
9. XM.
10. S3M.
11. MOD.

If a parser returns success, `ctx->format` is set to that parser's format and the overall result becomes success. After each parser attempt, the input is seeked to `ctx->restart`.

This means multiple parsers may contribute, notably ID3v2 and ID3v1 for MP3.

## Callback Wrapper

`tagscallcb()` trims leading/trailing ASCII control/space characters for normal string tags, invokes `ctx->tag()`, and updates `ctx->found` plus `ctx->num` for known tag types.

Binary tags such as images pass offset/size and optional stream filter function and are not string-trimmed.

## Risks

The dispatcher assumes the caller-provided `read`, `seek`, and `tag` callbacks are valid. It uses `ctx->restart` to coordinate parser chaining; individual parsers are responsible for setting that correctly when they consume leading metadata.
