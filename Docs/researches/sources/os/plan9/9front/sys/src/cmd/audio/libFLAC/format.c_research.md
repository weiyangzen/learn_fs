# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/format.c

## Purpose

This file defines public FLAC format constants, string tables, and validation/allocation helpers for metadata and entropy-coding structures. It is a central source of field widths, sync values, metadata type strings, subset checks, seektable sorting, UTF-8 validation, Vorbis comment validation, cuesheet validation, picture validation, and partitioned Rice contents management.

## Constants and Strings

The file exports:

- Version/vendor strings derived from git macros or `PACKAGE_VERSION`.
- Stream sync string/value and sync bit length.
- STREAMINFO, APPLICATION, SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE, metadata header, frame header/footer, entropy coding, and subframe field bit lengths.
- Seekpoint placeholder constant.
- Entropy coding method, subframe type, channel assignment, frame number type, metadata type, and picture type string tables.

These constants are used by bit readers/writers, metadata code, encoders, and decoders to keep serialized field sizes consistent.

## Format Validation

- `FLAC__format_sample_rate_is_valid()` rejects zero and values above `FLAC__MAX_SAMPLE_RATE`.
- `FLAC__format_blocksize_is_subset()` enforces subset block-size limits, including the stricter 4608-sample limit at sample rates up to 48 kHz.
- `FLAC__format_sample_rate_is_subset()` rejects invalid rates, rates too large for subset encoding, and high rates not divisible by 10 when required.
- `FLAC__format_seektable_is_legal()` checks monotonic non-placeholder seekpoint sample numbers.
- `FLAC__format_vorbiscomment_entry_name_is_legal()`, `_value_is_legal()`, and `_entry_is_legal()` validate field-name character ranges, `=` separation, and UTF-8 values.
- `FLAC__format_cuesheet_is_legal()` validates cue sheet track/index structure and optional CD-DA subset constraints such as lead-in, 588-sample divisibility, lead-out track number, and sequential indices.
- `FLAC__format_picture_is_legal()` validates printable ASCII MIME strings and UTF-8 descriptions.

The internal `utf8len_()` rejects invalid UTF-8, overlong forms, surrogate ranges, and selected noncharacters. It supports sequences up to six bytes because FLAC metadata historically permits that form.

## Seektable Sorting

`FLAC__format_seektable_sort()` qsorts seekpoints by sample number, removes duplicate non-placeholder sample numbers, moves retained entries to the front, and fills the tail with placeholder points with zero offset and frame sample count. It returns the number of unique non-duplicate entries retained before placeholders.

## Rice Partition Helpers

- `FLAC__format_get_max_rice_partition_order()` derives the maximum legal partition order from block size and predictor order.
- `FLAC__format_get_max_rice_partition_order_from_blocksize()` counts factors of two in the block size and caps at `FLAC__MAX_RICE_PARTITION_ORDER`.
- `FLAC__format_get_max_rice_partition_order_from_blocksize_limited_max_and_predictor_order()` reduces a proposed partition order until each partition can contain more samples than the predictor order.

## Partitioned Rice Contents Lifecycle

`FLAC__format_entropy_coding_method_partitioned_rice_contents_init()` zeroes pointers and capacity. `clear()` frees `parameters` and `raw_bits`. `ensure_size()` reallocates both arrays for `1 << max_partition_order` entries, zeroes `raw_bits`, and updates `capacity_by_order`.

## Integration Points

The file includes public `FLAC/format.h`, private `format.h`, `FLAC/assert.h`, allocation helpers, and macros. It is shared by stream encoder/decoder metadata handling, frame coding, and validation paths.

## Risks and Notes

`ensure_size()` updates `parameters` before allocating `raw_bits`; if the second reallocation fails, the object may have a resized parameters array but no matching raw-bits growth. Callers must treat a false return as a failed allocation state. The UTF-8 validator reads continuation bytes based on the leading byte, so callers must pass buffers with enough accessible bytes for the declared metadata length; bounded callers check `value != end` after advancing but the helper itself does not receive an end pointer.
