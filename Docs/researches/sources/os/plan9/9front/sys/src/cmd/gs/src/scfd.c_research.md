# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfd.c

Implements the `CCITTFaxDecode` stream filter. Initialization allocates current and optional previous line buffers, sets raster size and polarity, initializes Huffman decode state, and prepares row/EOL tracking.

The process routine manages row completion, output copying, EOL detection, optional damaged-row skipping, Group 3 1-D, Group 3 mixed 1-D/2-D, and Group 4 2-D modes. It decodes Huffman runs into packed output rows using macros for bit buffering, white/black run decoding, vertical/pass/horizontal 2-D modes, and black-bit inversion.

EOL scanning recognizes RTC/EOFB-style termination counts. 1-D decoding alternates white and black runs. 2-D decoding compares the current row with the previous reference row and handles pass, vertical, and horizontal modes.

Dependencies include `scf.h`, `scfx.h`, `strimpl.h`, `gdebug.h`, and generated decode tables from `scfdtab.c`.

Risk notes: uncompressed mode returns `ERRC` in the active code path, and comments mark some damaged-row and partial-code cases as not implemented. This is stream/image decompression code.
