# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/crc.c

## Purpose

This file implements FLAC CRC primitives. It contains the CRC-8 table used for frame headers, an eight-slice CRC-16 table used for frame data/footer checks, and functions for byte-buffer and word-buffer CRC updates.

## Data and Algorithms

- `FLAC__crc8_table[256]` implements CRC-8 with polynomial `x^8 + x^2 + x + 1` and initial value 0.
- `FLAC__crc16_table[8][256]` implements CRC-16 with polynomial `x^16 + x^15 + x^2 + 1` and initial value 0. The eight-table layout supports processing eight bytes at a time.
- A disabled `FLAC__crc16_init_table()` block documents how the CRC-16 table can be generated.

## Functions

- `FLAC__crc8(const FLAC__byte *data, uint32_t len)` iterates byte by byte through the CRC-8 table.
- `FLAC__crc16(const FLAC__byte *data, uint32_t len)` processes blocks of eight bytes using the sliced table, then handles remaining bytes with the base table.
- `FLAC__crc16_update_words32(const FLAC__uint32 *words, uint32_t len, FLAC__uint16 crc)` updates CRC from big-endian 32-bit words two at a time, with a one-word tail path.
- `FLAC__crc16_update_words64(const FLAC__uint64 *words, uint32_t len, FLAC__uint16 crc)` updates CRC from big-endian 64-bit words one at a time.

## Integration Points

The file includes `private/crc.h`. It is used by `bitreader.c` for running read CRC, by `bitwriter.c` for output CRC generation, and by frame parsing/encoding logic elsewhere.

## Risks and Notes

The word update functions assume words are already in the same big-endian logical order used by the bit reader/writer buffers. A mismatch in byte swapping before these calls would produce wrong frame CRCs even if byte-buffer CRCs remain correct.
