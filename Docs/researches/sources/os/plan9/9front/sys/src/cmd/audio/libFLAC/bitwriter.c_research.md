# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitwriter.c

## Purpose

This file implements libFLAC's internal buffered bit writer. It accumulates FLAC stream fields into a growable word buffer, writes raw signed/unsigned values, zero padding, little-endian metadata integers, byte blocks, unary codes, Rice-coded residuals, UTF-8-style frame/sample numbers, and computes CRCs over serialized byte-aligned output.

## Core Data Structures

`FLAC__BitWriter` stores:

- `buffer` and `capacity` for completed big-endian output words.
- `accum` for a partially filled word, with bits right-justified until flushed.
- `words` for completed words and `bits` for used bits in `accum`.

The word type is `FLAC__uint32` or `FLAC__uint64` depending on `ENABLE_64_BIT_WORDS`. Completed words are stored in stream byte order via `SWAP_BE_WORD_TO_HOST()`.

## Main Control Flow

`bitwriter_grow_()` expands the buffer when pending writes exceed capacity. It rounds growth to 4 KiB increments, uses `safe_realloc_nofree_mul_2op_()`, and refuses capacities larger than the maximum representable FLAC metadata block length to guard against impossible or corrupt size requests.

`FLAC__bitwriter_get_buffer()` requires byte alignment. If `accum` contains byte-aligned partial data, it appends a shifted copy as a temporary final word without changing `accum`/`bits`, then returns a byte pointer and byte count. `release_buffer()` is currently a no-op.

## Write Operations

- `FLAC__bitwriter_write_zeroes()` efficiently fills partial words, whole zero words, and trailing accumulator bits.
- `FLAC__bitwriter_write_raw_uint32_nocheck()` is the central raw writer and handles appending into the accumulator, flushing completed words, or writing a full word directly.
- Checked unsigned writers verify unused high bits are zero. Signed writers mask unused high bits before delegating.
- 64-bit writes split into high and low 32-bit pieces.
- `FLAC__bitwriter_write_raw_uint32_little_endian()` writes four bytes least-significant first for metadata fields.
- `FLAC__bitwriter_write_byte_block()` pre-grows and writes metadata byte arrays.
- `FLAC__bitwriter_write_unary_unsigned()` emits unary zeroes followed by a one.
- `FLAC__bitwriter_rice_bits()`, `FLAC__bitwriter_write_rice_signed()`, and `FLAC__bitwriter_write_rice_signed_block()` fold signed residuals to unsigned and emit partitioned Rice code words. The block writer has optimized paths for codes fitting within the current word.
- UTF-8 uint32/uint64 writers encode frame/sample numbers up to 31 bits and 36 bits respectively.
- `FLAC__bitwriter_zero_pad_to_byte_boundary()` writes zero bits until byte aligned.

## CRC Support

`FLAC__bitwriter_get_write_crc16()` and `FLAC__bitwriter_get_write_crc8()` serialize the current byte-aligned buffer, compute frame/footer or header CRCs with `private/crc.h`, then release the buffer.

## Integration Points

The writer depends on `private/bitwriter.h`, `private/crc.h`, `private/format.h`, `private/macros.h`, `private/stream_encoder.h`, `share/alloc.h`, `share/compat.h`, and `share/endswap.h`. It is central to metadata and frame construction in the encoder.

## Risks and Notes

The writer assumes byte alignment before buffer extraction and CRC calculation. Capacity checks are intentionally pessimistic in several hot paths. Correctness depends on preserving the accumulator invariant and swapping completed words exactly once. Rice block writing asserts `parameter < 31`, while single-value Rice writing accepts `parameter < 32`.
