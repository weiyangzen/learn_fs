# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writejpg.c

Baseline JPEG writer for Plan 9 images. It emits JFIF, optional comments, quantization tables, Huffman tables, SOF0, SOS, entropy-coded data, and EOI.

Input support covers gray depths and `RGB24`; grayscale channels force single-component JPEG. Encoding converts pixels to YCbCr, applies an integer FDCT, quantizes with built-in luminance/chrominance tables, builds canonical Huffman encode tables, and writes entropy-coded DC/AC coefficients with byte stuffing.

Public entry points are `writejpg` and `memwritejpg`. The `sflag` path changes quantization/zigzag handling, while `kflag` requests grayscale output.
