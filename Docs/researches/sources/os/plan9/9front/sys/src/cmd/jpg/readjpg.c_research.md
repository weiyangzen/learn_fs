# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readjpg.c

JPEG decoder for baseline and progressive Huffman JPEG. Public entry points are `Breadjpg` and `readjpg`, returning one `Rawimage` in a null-terminated array, with output in `CRGB`, `CYCbCr`, or `CY` depending on input and requested color space.

It parses markers and segments including SOI/EOI, APPn, DQT, DHT, SOF, SOF2, SOS, DRI, and COM. It builds Huffman fast lookup tables, reads quantization tables, decodes baseline MCUs, supports restart intervals, and handles progressive DC/AC scans with refinement before final IDCT.

Color output paths cover grayscale, direct 1x1 sampling, and general resampling. Error handling preserves partial images when possible and uses `longjmp` for fatal decode errors.
