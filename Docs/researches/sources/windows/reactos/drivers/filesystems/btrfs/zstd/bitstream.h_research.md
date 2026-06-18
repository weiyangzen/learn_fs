# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/bitstream.h

## Purpose

Inline bitstream encoder/decoder used by FSE and HUF. It writes bit fields forward into memory and reads them backward, matching FSE/HUF’s LIFO entropy stream model.

## Main Components

- Constants:
  - `STREAM_ACCUMULATOR_MIN_32`
  - `STREAM_ACCUMULATOR_MIN_64`
  - `STREAM_ACCUMULATOR_MIN`
- Compression stream state:
  - `BIT_CStream_t`
  - `BIT_initCStream`
  - `BIT_addBits`
  - `BIT_addBitsFast`
  - `BIT_flushBits`
  - `BIT_flushBitsFast`
  - `BIT_closeCStream`
- Decompression stream state:
  - `BIT_DStream_t`
  - `BIT_DStream_status`
  - `BIT_initDStream`
  - `BIT_readBits`
  - `BIT_readBitsFast`
  - `BIT_reloadDStream`
  - `BIT_reloadDStreamFast`
  - `BIT_endOfDStream`
- Internal helpers:
  - `BIT_highbit32`
  - `BIT_mask`
  - `BIT_lookBits`, `BIT_lookBitsFast`
  - `BIT_skipBits`

## Dependencies

- `mem.h` for unaligned little-endian reads/writes.
- `compiler.h` for branch hints.
- `debug.h` for assertions/logging.
- `error_private.h` for `ERROR(...)`.

## Behavior

- Encoder accumulates bits in a `size_t` register and flushes whole bytes to the destination buffer.
- `BIT_closeCStream` writes a one-bit end marker and returns zero if the destination overflowed.
- Decoder initializes from the last bytes of a stream, validates the end marker, and consumes fields in reverse order.
- Reload status distinguishes unfinished, end-of-buffer, completed, and overflow states.

## Research Notes

- The fast variants assume clean inputs and sufficient buffer/register space.
- Several callers rely on exact reverse-order semantics; changing bit layout would break FSE/HUF compatibility.
- Corruption handling depends on end marker validation and exact `BIT_endOfDStream` checks.
