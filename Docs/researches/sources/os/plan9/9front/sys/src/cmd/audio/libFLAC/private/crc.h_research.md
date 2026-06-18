# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/crc.h

## Role

`private/crc.h` declares CRC helpers for FLAC frame/header integrity checks.

## API Surface

- `FLAC__crc8()` computes the FLAC 8-bit CRC using polynomial `x^8 + x^2 + x + 1`.
- `FLAC__crc16_table[8][256]` is the exported lookup table for CRC16.
- `FLAC__CRC16_UPDATE(data, crc)` updates a CRC16 one byte at a time.
- `FLAC__crc16()` computes CRC16 over byte data.
- `FLAC__crc16_update_words32()` and `FLAC__crc16_update_words64()` update CRC16 over word buffers.

## Important Implementation Details

CRC16 uses polynomial `x^16 + x^15 + x^2 + 1`, MSB-shifted first, initial value zero. The macro masks to 16 bits after shifting.

## Risks / Edge Cases

Callers must feed bytes in stream order. Word-update helpers depend on the implementation's interpretation of word buffers and are intended for bitreader/bitwriter hot paths.

## Dependencies

Includes `FLAC/ordinals.h`.
