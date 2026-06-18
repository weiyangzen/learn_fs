# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_helper.h

## Role

`private/ogg_helper.h` declares helper functions for working with simple Ogg pages in seekable encoder paths.

## API Surface

It declares page lifecycle helpers `simple_ogg_page__init()` and `simple_ogg_page__clear()`, plus `simple_ogg_page__get_at()` and `simple_ogg_page__set_at()` for reading/writing an Ogg page at a stream position using encoder seek/read/write callbacks.

## Important Contracts

The caller supplies an `ogg_page` whose header/body fields are managed by these helpers. `get_at()` expects an initially empty page; `clear()` frees allocated header/body memory.

## Dependencies

Includes libogg and `FLAC/stream_encoder.h`.
