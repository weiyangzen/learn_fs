# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.h

This header declares the MP3 bitstream output interface.

Exports:
- `format_bitstream()`: encode one frame's side info and main data into the output bitstream.
- `flush_bitstream()`: pad and flush pending MP3 frame data.
- `add_dummy_byte()`: append a raw byte while adjusting queued header timing.
- `copy_buffer()`: copy completed bytes to a caller buffer and reset bitstream byte position.
- `init_bit_stream_w()`: allocate and initialize write-side bitstream state.
- `main_CRC_init()`: declared but implemented as an empty function in `bitstream.c`.

Dependencies:
- Includes `util.h`, which provides LAME internal structures and `III_scalefac_t`.

Integration:
- Used by `encoder.c`, `lame.c`, `VbrTag.c`, and `id3tag.c`.
- This is a central boundary between frame encoding and byte-oriented output.

Risks:
- The API exposes raw buffer sizes and requires callers to handle negative return codes from `copy_buffer()`.
