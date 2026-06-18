# File Research: sources/os/linux/linux/fs/squashfs/lzo_wrapper.c

Implements the LZO decompressor wrapper.

The stream owns vmalloc input and output buffers sized for the larger of SquashFS block size and metadata size. The wrapper copies BIO data into the input buffer, calls `lzo1x_decompress_safe()`, then copies decompressed output through the page actor.

Registers compressor id `LZO_COMPRESSION`, name `lzo`, supported, with no temporary direct-page buffer requirement.
