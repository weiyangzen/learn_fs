# File Research: sources/os/linux/linux/fs/squashfs/lz4_wrapper.c

Implements the LZ4 decompressor wrapper.

It requires LZ4 compression options and validates the legacy version expected by the kernel format. The stream allocates vmalloc input and output buffers sized to the max of filesystem block size and metadata block size.

Decompression copies BIO segments into the input buffer, calls `LZ4_decompress_safe()`, then copies output pages through the page actor.

Registers compressor id `LZ4_COMPRESSION`, name `lz4`, supported, with no direct-page temporary buffer requirement.
