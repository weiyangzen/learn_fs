# File Research: sources/os/linux/linux/fs/squashfs/xz_wrapper.c

Implements the XZ decompressor wrapper.

Compression options may specify dictionary size; the parser validates expected option length and dictionary-size shape, otherwise defaults to max(block size, metadata size).

The stream uses `xz_dec_init(XZ_PREALLOC, dict_size)`. Decompression resets the decoder, feeds BIO segments incrementally through `xz_dec_run()`, and writes output page-by-page via the page actor.

Registers compressor id `XZ_COMPRESSION`, name `xz`, supported, with `alloc_buffer = 1`.
