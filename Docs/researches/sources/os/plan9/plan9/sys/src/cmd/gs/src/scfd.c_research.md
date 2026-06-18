# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfd.c

Implementation of Ghostscript’s `CCITTFaxDecode` stream filter.

Core behavior:

- Initializes raster size, line buffers, optional previous-line buffer for 2-D modes, row counters, EOL counters, bit-reader state, and polarity.
- Copies completed decoded rows from internal line buffers to the caller.
- Handles Group 3/4 EOL detection, RTC/EOFB end conditions, optional byte alignment, mixed 1-D/2-D `K` handling, row limits, and damage-skipping scaffolding.
- Implements `cf_decode_1d` for white/black Huffman run decoding and scan-line bit filling.
- Implements `cf_decode_2d` for pass, vertical, and horizontal coding against a previous reference line.
- Uses generated decode tables from `scfdtab.c` and run-scan macros from `scf.h`.
- Keeps intermediate state so decoding can suspend and resume across input/output buffer boundaries.
- `cf_decode_uncompressed` currently returns `ERRC`; an alternative untested implementation is compiled out.

Risk notes: some source comments mark incomplete or questionable areas, including damaged row substitution and uncompressed mode handling. Allocation-failure comments are legacy “WRONG” markers but the code does return stream errors.

This is CCITT fax image decompression, not filesystem code.
