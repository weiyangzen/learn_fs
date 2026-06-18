# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/compress.c

Purpose: Implements bzip2 compression back-end machinery other than block sorting.

Key points:
- Provides bitstream output helpers: `BZ2_bsInitWrite`, `bsFinishWrite`, `bsW`, `bsPutUInt32`, and `bsPutUChar`.
- `generateMTFValues` converts sorted block data into move-to-front values with run-length coding and symbol frequencies.
- `sendMTFValues` chooses 2 to 6 Huffman groups based on MTF size, iteratively improves code lengths, MTF-encodes selectors, writes mapping tables, selectors, code lengths, and encoded MTF data.
- Fast paths are unrolled for the common six-group, 50-symbol block segment case.
- `BZ2_compressBlock` finalizes block CRCs, emits stream headers/trailers, block magic, CRC, non-randomized flag, original pointer, MTF/Huffman payload, and final combined CRC.

Dependencies and interactions:
- Requires block sorting via `BZ2_blockSort`.
- Calls Huffman helpers from `huffman.c`.
- Uses CRC macros and `EState` fields from `bzlib_private.h`.
- Produces compressed bytes into `EState.zbits`, which overlays the second work array.

Research notes:
- Modern randomization is disabled on output, but the format bit is still emitted for compatibility.
- Storage aliasing among `arr1`, `arr2`, `ptr`, `block`, `mtfv`, and `zbits` is intentional and important for memory footprint.
