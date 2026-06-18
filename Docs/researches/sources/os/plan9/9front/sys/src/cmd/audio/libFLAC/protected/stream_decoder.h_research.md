# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_decoder.h

## Role

`protected/stream_decoder.h` defines the internal/protected state visible to libFLAC decoder implementation files and declares an input-buffer introspection helper.

## Data Structure

`FLAC__StreamDecoderProtected` stores decoder state, init status, channel count, channel assignment, bits per sample, sample rate, current blocksize, MD5 checking flag, and optional Ogg decoder aspect state when `FLAC__HAS_OGG` is enabled.

## API Surface

It declares `FLAC__stream_decoder_get_input_bytes_unconsumed()`, returning the number of input bytes still buffered but unconsumed.

## Risks / Edge Cases

This is not public ABI. Any layout change affects internal files that access `decoder->protected_`. Ogg support conditionally changes the structure layout.

## Dependencies

Includes `FLAC/stream_decoder.h` and conditionally `private/ogg_decoder_aspect.h`.
