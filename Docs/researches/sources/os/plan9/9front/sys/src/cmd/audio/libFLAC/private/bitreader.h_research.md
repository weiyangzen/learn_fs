# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitreader.h

## Role

`private/bitreader.h` declares libFLAC's opaque buffered bit reader API. It is used by decoders to read FLAC bitstream fields, residual coding, byte-aligned metadata, frame numbers, and CRC-protected data.

## API Surface

The header declares lifecycle functions (`new`, `delete`, `init`, `free`, `clear`, `dump`), framesync bookmarking/rewind, CRC reset/get, alignment and limit introspection, and raw read operations.

Read operations include unsigned/signed 32-bit and 64-bit fields, little-endian 32-bit metadata values, skipped bits/bytes without CRC, byte-block reads, unary values, Rice-signed scalar/block values, and UTF-8-style uint32/uint64 reads.

## Important Contracts

`FLAC__BitReader` is opaque. Data arrives through `FLAC__BitReaderReadCallback`, which fills a byte buffer and updates a byte count. Several APIs explicitly do not update CRC when skipping or reading byte blocks, and callers must choose them only where appropriate.

## Risks / Edge Cases

- CRC APIs assume callers understand byte alignment and the implementation's read cursor behavior.
- Read limits can invalidate future reads if exceeded.
- UTF-8 frame-number decoders expose invalid encodings through output sentinel behavior in the implementation rather than only via return status.

## Dependencies

Includes `FLAC/ordinals.h` and `private/cpu.h`; implementation depends on bitmath, CRC, endian, and buffer management internals.
