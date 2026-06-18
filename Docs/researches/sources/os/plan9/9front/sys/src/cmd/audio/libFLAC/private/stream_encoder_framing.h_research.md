# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/stream_encoder_framing.h

## Role

`private/stream_encoder_framing.h` declares encoder serialization helpers that write FLAC metadata, frame headers, and subframes into a `FLAC__BitWriter`.

## API Surface

It declares:

- `FLAC__add_metadata_block()`
- `FLAC__frame_add_header()`
- `FLAC__subframe_add_constant()`
- `FLAC__subframe_add_fixed()`
- `FLAC__subframe_add_lpc()`
- `FLAC__subframe_add_verbatim()`

The subframe functions take subframe-specific data, sample counts or residual counts, bits per sample, wasted-bit count, and a bitwriter.

## Risks / Edge Cases

These helpers are format-critical. Caller-provided frame/subframe structures must already satisfy FLAC constraints, including valid residual sample counts and wasted-bit metadata.

## Dependencies

Includes `FLAC/format.h` and `private/bitwriter.h`.
