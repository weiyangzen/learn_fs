# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/ogg_encoder_aspect.h

## Role

`private/ogg_encoder_aspect.h` defines the Ogg encoder aspect state and callback wrapper used to package native FLAC encoder output into Ogg FLAC streams.

## Data Structures

`FLAC__OggEncoderAspect` stores serial number, metadata header count, libogg stream state, a reusable page, whether native `fLaC` magic has been seen, whether the next packet is first, and accumulated samples written.

## API Surface

It declares serial and metadata-count setters, defaults/init/finish functions, a write callback proxy type, and `FLAC__ogg_encoder_aspect_write_callback_wrapper()`.

## Risks / Edge Cases

`num_metadata` must fit in the Ogg FLAC 16-bit header count field. State fields assume a specific sequence of native FLAC encoder write callbacks.

## Dependencies

Includes libogg, `FLAC/ordinals.h`, and `FLAC/stream_encoder.h`.
