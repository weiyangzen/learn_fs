# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_decoder_aspect.c

## Role

`ogg_decoder_aspect.c` adapts libogg page/packet decoding to libFLAC's pull-style decoder read callback. It keeps Ogg stream/sync state, extracts packets from pages, validates the Ogg FLAC mapping header, and feeds FLAC bytes back to the native decoder in bounded chunks.

## Major Functions

- `FLAC__ogg_decoder_aspect_set_defaults()` defaults to using the first observed Ogg serial number.
- `FLAC__ogg_decoder_aspect_init()` initializes `ogg_stream_state` and `ogg_sync_state`, marks mapping version unknown, and resets page/packet state.
- `finish()`, `flush()`, and `reset()` clear or reset Ogg state.
- `set_serial_number()` forces a caller-specified stream serial.
- `FLAC__ogg_decoder_aspect_read_callback_wrapper()` is the core bridge from client reads to FLAC decoder bytes.

## Important Implementation Details

The read wrapper loops until it fills the FLAC-requested byte count, hits end-of-stream, or returns an error. It preserves a working Ogg page and packet across calls so packets can be split across libFLAC read buffers. It reads client data into `ogg_sync_buffer()` in chunks of at least 8192 bytes or the remaining FLAC request size.

On the first Ogg FLAC header packet, it checks packet type `0x7f`, magic `"FLAC"`, mapping version major/minor, and rejects non-major-version-1 streams. After validating the mapping prefix, it advances the packet pointer so libFLAC sees the embedded native `fLaC` stream bytes.

## Risks / Edge Cases

- `working_packet.packet` is advanced in place while bytes are consumed; code using the same packet later must respect the shortened view.
- Lost sync and unsupported mapping versions are surfaced as distinct aspect statuses.
- If `use_first_serial_number` is active, the first page serial is written directly into `stream_state.serialno`.
- Ogg pages from another stream are ignored when `ogg_stream_pagein()` rejects them.
- The wrapper can read more from the client than the immediate FLAC byte request to obtain complete Ogg pages.

## Dependencies

Uses libogg, `private/ogg_decoder_aspect.h`, `private/ogg_mapping.h`, `private/macros.h`, and `FLAC/assert.h`.
