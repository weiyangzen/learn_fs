# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/protected/stream_encoder.h

## Role

`protected/stream_encoder.h` defines the internal/protected encoder state used by libFLAC implementation files.

## Data Structures

When floating-point analysis is enabled, it defines `FLAC__ApodizationFunction` and `FLAC__ApodizationSpecification`, covering supported window families and their parameters.

`FLAC__StreamEncoderProtected` stores encoder state and configuration: verification, subset mode, MD5, stereo mode flags, channel/sample parameters, apodization specs, LPC/QLP settings, residual partition settings, Rice search distance, total sample estimate, min-bitrate flag, metadata pointers/count, stream offsets, and optional Ogg encoder aspect state.

## Risks / Edge Cases

- The structure is internal but widely used by implementation code via `encoder->protected_`.
- Ogg and integer-only build macros change layout.
- `metadata` is an array of metadata pointers; lifetime management must be coordinated with public encoder APIs.

## Dependencies

Includes `FLAC/stream_encoder.h`, optionally `private/ogg_encoder_aspect.h`, and `private/float.h` for apodization specs.
