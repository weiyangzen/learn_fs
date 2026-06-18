# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_encoder_aspect.c

## Role

`ogg_encoder_aspect.c` adapts libFLAC stream encoder write callbacks into Ogg FLAC packets and pages. It recognizes the native `fLaC` magic callback, combines it with STREAMINFO into the required first Ogg FLAC header packet, then packetizes metadata and audio frames.

## Major Functions

- `FLAC__ogg_encoder_aspect_set_defaults()` initializes default serial number and metadata count.
- `init()` initializes libogg stream state and packet bookkeeping.
- `finish()` clears libogg stream state.
- `set_serial_number()` and `set_num_metadata()` configure stream serial and header packet count.
- `FLAC__ogg_encoder_aspect_write_callback_wrapper()` converts FLAC write callback buffers into Ogg packets and invokes the client write callback for page header/body output.

## Important Implementation Details

The implementation depends on encoder behavior where the `fLaC` magic arrives as one metadata write callback, followed by STREAMINFO as a separate callback. The first actual Ogg packet is synthetic: packet type, `"FLAC"` mapping magic, version 1.0, two-byte metadata header count, native `fLaC`, and STREAMINFO header/data.

Metadata packets are flushed with `ogg_stream_flush()` so metadata lands promptly in pages. Audio packets use `ogg_stream_pageout()`. `packet.granulepos` is set to `samples_written + samples`; `samples_written` is updated after each wrapper call.

## Risks / Edge Cases

- If encoder callback ordering changes, the wrapper asserts and returns fatal error.
- `set_num_metadata()` rejects values that do not fit the 16-bit Ogg FLAC header count field.
- Page header and body are written with separate client write callback invocations.
- The function passes `samples=0` to the downstream write callback for Ogg page output because page-level sample accounting is not directly mapped.
- `finish()` notes an unresolved comment about the stored page object, though libogg owns stream state cleanup.

## Dependencies

Uses libogg, `private/ogg_encoder_aspect.h`, `private/ogg_mapping.h`, and public stream encoder status definitions.
