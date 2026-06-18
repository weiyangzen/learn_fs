# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writetif.c

TIFF writer for libdraw `Image` and `Memimage`. It writes big-endian TIFF, builds IFD fields, strip offsets/counts, optional descriptions, resolution rationals, palettes, and compressed or uncompressed image data.

Supported output channels include gray, colormap, and BGR24. Compression support includes none, CCITT Huffman/T4/T6 fax, LZW with optional horizontal predictor, and PackBits. Fax paths force photometric white-zero bilevel output.

The file contains fax run-code tables and 1D/2D encoders, LZW hash encoder, PackBits row encoder, strip planning, palette creation from `cmap2rgb`, and field serialization. Public entry points are `writetif` and `memwritetif`.
