# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readtif.c

TIFF reader implementing endian-aware IFD parsing, strip loading, decompression, and conversion to Plan 9 `Rawimage`. Public entry points are `Breadtif` and `readtif`, accepting only `CRGB24` as requested color space.

Supported image classes include bilevel/gray, RGB, and palette TIFF with depths 1, 4, 8, and 24. Supported compression includes none, CCITT Huffman/T4/T6 fax, LZW with horizontal predictor, and PackBits. It requires orientation 1, planar configuration 1, valid strip offsets/counts, and compatible samples/photometric fields.

The file contains full fax white/black/mode code tables, 1D/2D fax decoders, LZW table expansion, predictor reversal, PackBits expansion, and palette/gray/RGB decode paths. It uses `werrstr` for validation failures and `sysfatal` for some low-level read/allocation failures.
