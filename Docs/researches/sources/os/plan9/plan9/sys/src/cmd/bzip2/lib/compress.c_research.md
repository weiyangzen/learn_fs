# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/compress.c

Compression back end excluding block sorting. It implements bitstream output helpers, byte-use mapping, MTF/RLE generation, adaptive selector/Huffman table generation, and final block/stream emission.

`generateMTFValues` converts sorted BWT block output into MTF symbols, encoding runs of zero MTF values as `BZ_RUNA/BZ_RUNB` and collecting frequencies. `sendMTFValues` chooses 2-6 Huffman groups based on MTF count, iteratively refines tables, MTF-encodes selectors, writes mapping bits, selectors, code lengths, and compressed MTF data.

`BZ2_compressBlock` finalizes block CRC, updates combined CRC, calls `BZ2_blockSort`, emits stream magic on the first block, emits block magic/CRC/randomised-bit/origPtr/data for nonempty blocks, and emits end magic plus combined CRC for the final block.
