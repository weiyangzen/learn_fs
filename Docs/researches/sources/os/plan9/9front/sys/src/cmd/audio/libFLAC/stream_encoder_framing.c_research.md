# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_encoder_framing.c

## Purpose

This file serializes FLAC metadata blocks, frame headers, and subframes into a `FLAC__BitWriter`. It is the low-level syntax writer used by `stream_encoder.c` after that file has selected metadata, frame parameters, channel assignments, subframe types, predictor data, and entropy parameters.

## Metadata Serialization

`FLAC__add_metadata_block()` writes a complete FLAC metadata block:

- Writes the `is_last` flag, metadata type, and metadata length.
- Adjusts Vorbis comment length to substitute the library vendor string.
- Serializes all known block types:
  - STREAMINFO: block sizes, frame sizes, sample rate, channels, bits per sample, total samples, MD5.
  - PADDING: zero bytes.
  - APPLICATION: application ID plus payload.
  - SEEKTABLE: sample number, stream offset, and frame sample count per point.
  - VORBIS_COMMENT: vendor string and user comments in little-endian length-prefixed form.
  - CUESHEET: catalog, lead-in, CD flag, tracks, ISRCs, and indices.
  - PICTURE: type, MIME, description, dimensions, color info, and image bytes.
  - Unknown metadata: raw payload bytes.
- Ensures output remains byte-aligned.

The STREAMINFO total sample field is written as zero if it exceeds the field width.

## Frame Header Serialization

`FLAC__frame_add_header()` writes a FLAC frame header:

- Writes sync code, reserved bit, and blocking strategy.
- Encodes blocksize using standard FLAC hints when possible, or writes extra 8/16-bit blocksize fields for uncommon sizes.
- Encodes sample rate using standard hints, or extra 8/16-bit sample-rate fields for custom rates.
- Encodes channel assignment: independent, left-side, right-side, or mid-side.
- Encodes bits per sample, reserved zero pad, and frame/sample number as UTF-8 integer.
- Appends the frame-header CRC-8.

The caller is responsible for giving a valid `FLAC__FrameHeader`; this function asserts invariants and returns false on bitwriter failure.

## Subframe Serialization

The file provides one writer per subframe type:

- `FLAC__subframe_add_constant()` writes subframe type, optional wasted-bits unary count, and the constant sample value.
- `FLAC__subframe_add_fixed()` writes type/order, wasted bits, warmup samples, entropy coding method, and fixed residual.
- `FLAC__subframe_add_lpc()` writes type/order, wasted bits, warmup samples, QLP precision, quantization shift, QLP coefficients, entropy coding method, and LPC residual.
- `FLAC__subframe_add_verbatim()` writes type, wasted bits, and raw samples, supporting both 32-bit and 33-bit verbatim data paths.

All subframe writers return `false` on any bitwriter write failure.

## Entropy Coding Helpers

`add_entropy_coding_method_()` writes the entropy method type and partition order for partitioned Rice or Rice2. Other types assert as unsupported.

`add_residual_partitioned_rice_()` writes partitioned residual data:

- Selects Rice parameter field width and escape value depending on normal Rice versus Rice2.
- For partition order 0, writes a single parameter and encodes all residuals, or writes escape raw bits.
- For higher partition orders, iterates partitions, subtracting predictor warmup samples from partition 0, then writes either Rice-coded residual blocks or raw escape-coded residuals.
- Uses `FLAC__bitwriter_write_rice_signed_block()` for normal Rice coding and raw signed integer writes for escape partitions.

## Key Dependencies

- `private/stream_encoder_framing.h` for exported framing declarations.
- `private/crc.h` and bitwriter CRC support for frame header CRC.
- `FLAC/assert.h`, `share/compat.h`, and public format constants/macros.

## Research Notes

This file does not choose compression models; it faithfully serializes structures prepared by `stream_encoder.c`. The main correctness sensitivities are exact FLAC field widths, byte alignment, Vorbis-comment vendor length adjustment, partition-0 predictor-order handling, and Rice versus Rice2 escape parameter widths.
