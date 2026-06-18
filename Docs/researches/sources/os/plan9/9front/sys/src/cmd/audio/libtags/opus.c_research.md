# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/opus.c

## Role

This file parses Ogg Opus headers, OpusTags comments, and approximate stream duration.

## Main Interface

`tagopus(Tagctx *ctx)` is the Opus parser called by `tagsget()`.

## Header and Tag Parsing

The parser reads the first two Ogg pages manually. It validates the `OggS` capture pattern, reads segment counts and lacing bytes, and detects:

- `OpusHead`: validates version 1, sets channel count from byte 1, and reads the input sample rate field.
- `OpusTags`: records the end of the tag packet and breaks into comment parsing.

It then reads the vendor length, skips the vendor string, reads the comment count, and parses `key=value` strings through `cbvorbiscomment()`.

The file has a FIXME noting embedded pictures can make tags span multiple packets; it stops when a comment would exceed the recorded packet end.

## Duration

If sample rate was identified, the parser scans near the beginning to find the first Ogg page granule position and near EOF to find a later page granule position. It computes duration using Opus's fixed 48 kHz granule position clock.

## Risks

This is a lightweight parser and does not use libogg. It assumes the initial headers and tags are in the first few pages and does not fully support multi-packet embedded pictures.
