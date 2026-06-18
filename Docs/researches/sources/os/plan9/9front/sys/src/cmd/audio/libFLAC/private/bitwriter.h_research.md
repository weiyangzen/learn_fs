# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitwriter.h

## Role

`private/bitwriter.h` declares libFLAC's opaque buffered bit writer API. Encoders use it to serialize metadata, frame headers, subframes, residuals, UTF-8-style numbers, and CRC-covered frame data.

## API Surface

The header declares lifecycle functions, CRC generation for CRC16 and CRC8, byte-alignment and unconsumed-bit introspection, direct buffer access with get/release, and bit-level write functions.

Write functions cover zero padding, raw signed/unsigned 32-bit and 64-bit values, little-endian 32-bit values, byte blocks, unary values, Rice bit estimation, Rice-signed scalar/block encoding, UTF-8-style uint32/uint64 encoding, and zero-padding to a byte boundary.

## Important Contracts

`FLAC__BitWriter` is opaque. Direct buffer access requires byte alignment, and no intervening bitwriter calls are allowed between `get_buffer()` and `release_buffer()`. CRC functions are non-const because they may materialize the buffer.

## Risks / Edge Cases

- The caller must respect buffer ownership; the returned direct buffer remains owned by the bitwriter.
- Bit-width arguments must match FLAC field constraints; enforcement is mostly in implementation and assertions.
- Rice/Golomb unused declarations are left disabled with `#if 0`.

## Dependencies

Includes `FLAC/ordinals.h` and standard `stdio.h` for dump output.
