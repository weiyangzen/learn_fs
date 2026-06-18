# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/bitreader.c

## Purpose

This file implements libFLAC's internal buffered bit reader. It reads big-endian FLAC bitstream fields from a client callback into 32-bit or 64-bit word buffers, supports raw integer extraction, byte-aligned block reads/skips, unary and Rice-coded residual decoding, UTF-8-style frame number decoding, frame CRC tracking, read limits, and rewinding after a remembered framesync position.

## Core Data Structures

`FLAC__BitReader` stores:

- `buffer`, `capacity`, `words`, and `bytes` for a word-array buffer plus incomplete tail bytes.
- `consumed_words` and `consumed_bits` for the read cursor.
- `read_crc16`, `crc16_offset`, and `crc16_align` for incremental frame CRC over consumed byte-aligned data.
- `read_limit_set` and `read_limit` for bounded reads.
- `last_seen_framesync` for recovery after sync search.
- `read_callback` and `client_data` for source I/O.

The word type is `FLAC__uint32` unless `ENABLE_64_BIT_WORDS` is enabled, in which case it is `FLAC__uint64`. Endianness is normalized with `ENDSWAP_32` or `ENDSWAP_64` so buffer words represent big-endian stream order.

## Main Control Flow

`bitreader_read_from_client_()` compacts unconsumed data, updates CRC for consumed full words, chooses the target byte region, handles partial tail word byte swapping on little-endian hosts, calls the client read callback, swaps newly filled words into host representation, updates `words` and `bytes`, and invalidates the remembered framesync position.

Construction and lifecycle functions allocate, initialize, clear, free, and dump the reader. `FLAC__bitreader_set_framesync_location()` records a byte location derived from the current cursor, and `FLAC__bitreader_rewind_to_after_last_seen_framesync()` either rewinds to just after that byte or resets to the start if no sync was recorded.

## Read Operations

- `FLAC__bitreader_read_raw_uint32()` is the central bit extraction path. It enforces read limits, refills until enough bits exist, then reads across consumed head words or partial tail words.
- Signed 32/64 reads call the unsigned routines and sign-extend with a fixed-width bit trick.
- `FLAC__bitreader_read_raw_uint64()` composes high and low chunks when more than 32 bits are requested.
- `FLAC__bitreader_read_uint32_little_endian()` reads four bytes and assembles a little-endian 32-bit integer for metadata such as Vorbis comments.
- Byte-aligned skip/read functions optimize whole-word movement after aligning through any partial head word.
- `FLAC__bitreader_read_unary_unsigned()` scans for the unary stop bit with count-leading-zero helpers.
- `FLAC__bitreader_read_rice_signed_block()` is the hot residual decode path. It keeps cursor state in locals, decodes unary MSBs plus binary LSBs, checks a maximum MSB limit for int32 residual bounds, and falls back to the generic reader when a code spans unavailable data.
- UTF-8 uint32/uint64 readers decode FLAC frame/sample numbers, optionally copying raw bytes, and signal invalid encodings through all-ones sentinel values while returning true if bytes were successfully read.

## CRC and Limits

`FLAC__bitreader_reset_read_crc16()` starts CRC at a byte-aligned cursor. `FLAC__bitreader_get_read_crc16()` updates full consumed words and tail bytes up to the current byte-aligned cursor. Read limits decrement in raw and byte-block operations; when a read would exceed the limit, the code invalidates the limit by setting it to all ones and returns false.

## Integration Points

The reader depends on `private/bitmath.h`, `private/bitreader.h`, `private/crc.h`, `private/macros.h`, `FLAC/assert.h`, `share/compat.h`, and `share/endswap.h`. It is a decoder-side primitive for parsing FLAC metadata, frame headers, subframes, residuals, and CRC-protected frame data.

## Risks and Notes

The most sensitive areas are partial-word handling on little-endian hosts, synchronization between cursor movement and CRC offsets, and the optimized Rice block decoder's local cursor updates. Several assertions require word sizes of at least 32 bits. The code assumes callers respect byte alignment for CRC and byte-block APIs. Invalid UTF-8-style frame numbers are represented by sentinel values rather than a false return.
