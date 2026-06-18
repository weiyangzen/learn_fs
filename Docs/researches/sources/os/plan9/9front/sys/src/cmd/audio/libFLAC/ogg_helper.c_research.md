# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/ogg_helper.c

## Role

`ogg_helper.c` provides helpers for reading, validating, clearing, and rewriting "simple" Ogg pages during seekable Ogg FLAC encoding. A simple page here means a page containing one complete packet, no continuation, zero granule position, and valid checksum.

## Major Functions

- `full_read_()` repeatedly calls the encoder read callback until a requested byte count is satisfied or an error/status transition occurs.
- `simple_ogg_page__init()` zeroes an `ogg_page`.
- `simple_ogg_page__clear()` frees page header/body allocations and reinitializes.
- `simple_ogg_page__get_at()` seeks to a position, reads an Ogg page header/table/body, validates simple-page structure, and checks CRC.
- `simple_ogg_page__set_at()` seeks to a position, updates page checksum, and rewrites header/body.

## Important Implementation Details

`simple_ogg_page__get_at()` reads the 27-byte fixed Ogg header, uses byte 26 to determine segment table length, and computes body length from lacing values. It verifies `"OggS"`, rejects continued packets, requires zero granule position, and rejects zero-sized packets. The final lacing byte may be less than 255, and all prior lacing bytes must be 255 to represent one packet.

CRC validation saves the four checksum bytes, calls `ogg_page_checksum_set()`, and compares the computed checksum against the saved bytes. Error states are reported through `encoder->protected_->state`.

## Risks / Edge Cases

- On read failures after allocating `page->header` or `page->body`, the caller must clear the page to avoid leaks.
- It only accepts simple one-packet pages and intentionally rejects valid but more complex Ogg pages.
- Callback `END_OF_STREAM` with zero bytes while more bytes are required is treated as Ogg error.
- Seek callback absence or non-OK seek status causes failure; seek errors set client error state.

## Dependencies

Uses libogg, `share/alloc.h`, `private/ogg_helper.h`, and `protected/stream_encoder.h`.
