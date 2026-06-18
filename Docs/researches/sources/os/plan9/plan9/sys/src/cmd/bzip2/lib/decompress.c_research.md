# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/decompress.c

Core bzip2 decompression state machine. `BZ2_decompress(DState*)` incrementally reads the compressed bitstream and can return `BZ_OK` when input is exhausted, saving local state fields in `DState` for later resumption.

It validates stream magic, allocates fast or small-memory inverse-BWT storage, reads block/end headers, block CRC, randomisation bit, original pointer, byte mapping, selectors, Huffman code lengths, builds decode tables, decodes MTF/RLE data into block storage, checks block bounds, and prepares inverse BWT traversal.

Fast mode builds `tt`; small mode uses `ll16` plus packed `ll4` with pointer reversal. It recognizes stream trailer magic, reads stored combined CRC, sets idle state, and returns `BZ_STREAM_END`. Data validation returns `BZ_DATA_ERROR` or `BZ_DATA_ERROR_MAGIC`.
