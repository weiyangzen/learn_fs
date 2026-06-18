# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_decoder_aspect.h

## Role

`private/ogg_decoder_aspect.h` defines the Ogg decoder aspect state and status API used to add Ogg FLAC support around the native stream decoder.

## Data Structures

`FLAC__OggDecoderAspect` stores API-configurable serial behavior, libogg stream and sync state, parsed mapping version, serial-number discovery state, end-of-stream state, current working page, and current working packet. The packet pointer and byte count are intentionally mutable as packet data is consumed.

## API Surface

The header declares serial/default/init/finish/flush/reset functions and `FLAC__ogg_decoder_aspect_read_callback_wrapper()`.

`FLAC__OggDecoderAspectReadStatus` distinguishes OK, end-of-stream, lost sync, not-FLAC, unsupported mapping version, abort, generic error, and memory allocation error.

## Risks / Edge Cases

This stateful adapter is sensitive to correct reset behavior. If callers reuse a decoder with first-serial-number mode, `reset()` re-enables serial discovery.

## Dependencies

Includes libogg, `FLAC/ordinals.h`, and `FLAC/stream_decoder.h`.
