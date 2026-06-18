# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libogg/ogg/ogg.h

## Role

This is the public libogg header used by the vendored Ogg implementation and codec users in the 9front audio tree. It defines Ogg data structures and declares the bit packing, stream framing, sync, page, and packet APIs.

It also includes a Plan 9 `#pragma lib` for linking `/sys/src/cmd/audio/libogg/libogg.a$O`.

## Main Types

The header defines:

- `ogg_iovec_t`: base pointer plus length for vectorized packet input.
- `oggpack_buffer`: bitstream packing state, including current byte/bit offsets, buffer pointer, and storage size.
- `ogg_page`: header/body pointer pair for an Ogg page.
- `ogg_stream_state`: logical stream encode/decode state, including body FIFO, lacing FIFO, granule positions, page counter, packet counter, serial number, and BOS/EOS state.
- `ogg_packet`: packet pointer plus length, BOS/EOS flags, granule position, and packet number.
- `ogg_sync_state`: raw byte sync buffer and page-discovery state.

## API Surface

The declarations are grouped as:

- Bitstream primitives: `oggpack_*` and `oggpackB_*`.
- Encoding primitives: packet input and page output/flush.
- Decoding primitives: sync buffer/pageout, stream pagein, packetout/peek.
- General stream lifecycle: init, clear, reset, reset serial number, destroy, check, EOS.
- Page helpers: checksum, flags, granule position, serial number, page number, packet count.
- Packet cleanup: `ogg_packet_clear()`.

## Dependencies

The file includes `stddef.h` and `ogg/os_types.h`. Memory allocation is abstracted by macros in `os_types.h`, while integer aliases are defined there.

## Integration Notes

This header is consumed by `bitwise.c`, `framing.c`, libvorbis, and other audio code that needs Ogg packet/page handling. Its structures are public and ABI-sensitive; changes to layout affect all linked users.
