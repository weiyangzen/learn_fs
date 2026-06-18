# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lz4_wrapper.c

Implements LZ4 compressor support.

Supported options:
- `-Xhc`
- `-Xacceleration <1..65537>`
- `-Xcompression-level <1..12>` for high-compression mode

Behavior:
- Tracks global option state: high-compression flag, acceleration, compression level, and whether options were explicitly supplied.
- Rejects incompatible options in postprocessing: acceleration with high-compression, or compression-level without high-compression.
- Dumps versioned LZ4 option structures. LZ4 always writes an option structure to identify the legacy stream format.
- Supports v1 options for legacy/high-compression flag and v2 options for non-default acceleration/compression data.
- Extracts options for append mode and checks options for unsquashfs compatibility.
- Compresses with either normal LZ4 or LZ4 HC wrappers selected by library version macros.
- Decompresses with `LZ4_decompress_safe()`.

Compatibility:
- `OLD_LIBRARY_OPTION` and `OLD_LIBRARY_EXTRACT` reject non-default acceleration when linked against older LZ4 APIs.

Notable quirks:
- Extraction paths do not explicitly clear all previous global option flags in every branch, so correctness assumes append/extract state is not contaminated by earlier option parsing.
