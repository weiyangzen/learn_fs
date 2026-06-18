# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.c

This file implements MP3 bitstream assembly for the LAME-derived encoder.

Key responsibilities:
- Writes individual bits and bytes into the encoder output buffer.
- Delays and inserts MPEG frame headers/side information at scheduled bit positions.
- Encodes MPEG Layer III side information with optional CRC.
- Huffman-encodes quantized spectral coefficients and count1 regions.
- Writes scalefactors for MPEG-1 and MPEG-2/LSF layouts.
- Drains reservoir/ancillary bits and flushes the stream.
- Copies completed bytes to caller-owned output buffers.

Important functions:
- `putheader_bits()`: copies a queued frame header into the bitstream.
- `putbits2()`: writes bits while honoring pending header insertion timing.
- `putbits_noheaders()`: writes bits while ignoring header insertion, used for dummy bytes/tags.
- `drain_into_ancillary()`: writes stuffing bits, beginning with `LAME` and version text where space allows.
- `writeheader()` and `CRC_writeheader()`: write header fields and update CRC.
- `encodeSideInfo2()`: serializes MPEG header and side information for MPEG-1 or MPEG-2.
- `HuffmanCode()`, `Huffmancodebits()`, `ShortHuffmancodebits()`, `LongHuffmancodebits()`: emit Huffman-coded spectral pairs.
- `writeMainData()`: writes scalefactors and Huffman data for all granules/channels.
- `format_bitstream()`: combines ancillary pre-drain, side info, main data, post-drain, reservoir accounting, and overflow protection.
- `flush_bitstream()`: pads enough bits to write all pending headers and complete the last frame.
- `add_dummy_byte()`: writes a raw byte and shifts all queued header timings.
- `copy_buffer()`: copies buffered bytes out and resets byte position.
- `init_bit_stream_w()`: allocates and initializes `gfc->bs`.

Dependencies and integration:
- Includes `tables.h`, `bitstream.h`, `quantize.h`, `quantize_pvt.h`, and `version.h`.
- Depends on `III_side_info_t`, `III_scalefac_t`, Huffman table `ht`, bitrate/frame-size helpers, and LAME internal flags.
- Called from `encoder.c` after quantization and from `lame.c` during initialization/flushing.
- `id3tag.c` and `VbrTag.c` use `add_dummy_byte()` to inject metadata bytes into the bitstream.

Notable state:
- `Bit_stream_struc` fields: buffer pointer, byte index, bit index, and total bit count.
- Header ring buffer fields in `gfc->header[]`, controlled by `h_ptr` and `w_ptr`.
- `l3_side->main_data_begin` and `gfc->ResvSize` must remain consistent.

Risks and edge cases:
- Many assertions verify bitcount invariants; in non-assert builds mismatches may only log through `ERRORF`.
- `init_bit_stream_w()` does not check `malloc()` failure.
- `copy_buffer()` returns `-1` if caller buffer is too small, but callers must propagate that correctly.
- The file mutates `table_select` values of 14 to 16 before writing side info.
- `bs->totbit` is reset after exceeding one billion bits to avoid overflow, adjusting queued header timings.
