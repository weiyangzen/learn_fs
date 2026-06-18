# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfe.c

Implements the `CCITTFaxEncode` stream filter. Initialization allocates current row, optional previous row, and encoded-line buffers; computes raster and worst-case encoded byte size; initializes Huffman encoder state; and prepares mixed 1-D/2-D row cadence.

The process routine collects full input scan lines, normalizes row-end sentinel bits for run scanners, writes optional EOL/byte alignment, encodes the row directly to the caller buffer or internal line buffer, swaps current/reference rows in 2-D modes, and emits final end-of-block EOL sequences.

`cf_encode_1d` alternates white and black run detection and emits run Huffman codes. `cf_encode_2d` compares current and previous rows and chooses pass, vertical, or horizontal coding. Long runs are split into make-up and termination codes.

Dependencies include `scf.h`, `scfx.h`, `strimpl.h`, generated/static tables from `scfetab.c`, and bit-run macros.

This is fax image compression stream logic.
