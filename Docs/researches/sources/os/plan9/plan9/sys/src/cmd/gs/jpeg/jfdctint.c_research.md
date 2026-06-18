# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jfdctint.c

Slow-but-accurate integer forward DCT implementation, compiled when `DCT_ISLOW_SUPPORTED` is enabled. It is specialized to `DCTSIZE == 8` and intentionally fails compilation otherwise.

The single exported routine is `jpeg_fdct_islow(DCTELEM *data)`, which performs an in-place 8x8 forward DCT using the Loeffler/Ligtenberg/Moschytz alternate method with fixed-point arithmetic. It processes rows first, then columns, leaving the final results scaled by the IJG convention so later quantization removes the remaining factor of 8.

The file defines fixed-point constants for `CONST_BITS == 13`, chooses `PASS1_BITS` based on sample precision, and uses `MULTIPLY16C16` for 8-bit builds. The arithmetic is carefully arranged to avoid multiple multiplications along one data path and to keep 32-bit intermediates within bounds.
