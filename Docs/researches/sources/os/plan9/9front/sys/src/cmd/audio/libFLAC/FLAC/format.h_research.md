# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/format.h

Public libFLAC format model header for in-memory FLAC stream, frame, subframe, and metadata structures.

Important contents:
- Defines FLAC format limits: metadata type range, block size range, channel count, bits per sample, sample rate, LPC order, Rice partition order, fixed predictor order, and FLAC subset limits.
- Declares library/version/vendor/sync constants such as `FLAC__VERSION_STRING`, `FLAC__VENDOR_STRING`, `FLAC__STREAM_SYNC_STRING`, and bit-length constants.
- Defines entropy coding structures for partitioned Rice and Rice2 residual coding.
- Defines subframe structures for constant, verbatim, fixed predictor, and LPC subframes, including warmup samples, residual pointers, QLP coefficients, and wasted-bit metadata.
- Defines frame structures: channel assignment, frame number/sample number union, frame header CRC-8, frame footer CRC-16, and `FLAC__Frame`.
- Defines all FLAC metadata block structures: STREAMINFO, PADDING, APPLICATION, SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE, UNKNOWN, and the polymorphic `FLAC__StreamMetadata`.
- Declares format validation/manipulation helpers for sample rates, FLAC subset constraints, Vorbis comments, seek tables, cue sheets, and picture blocks.

Implementation notes:
- This is a declaration-only API header. It does not implement parsing, decoding, allocation, or I/O.
- The file documents the local convention that `_LEN` constants are bit lengths while `_LENGTH` macros are byte lengths.
- Many structures intentionally expose raw pointers. The header describes representation, not ownership; object-level ownership helpers are declared in `metadata.h`.
- It includes `export.h` for public symbol visibility and `ordinals.h` for fixed-width FLAC integer aliases.
- The structures are ABI-facing public libFLAC data contracts, so field order and type choices are significant to users of this bundled library.

Filesystem relevance:
- No filesystem logic is present. Its relevance to this subset is indirect: it is vendored third-party audio codec API code under the 9front source tree, used by 9front audio commands rather than OS/VFS code.
