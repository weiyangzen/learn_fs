# File Research: sources/os/linux/linux/fs/squashfs/decompressor.c

Implements compressor-id dispatch and shared decompressor setup.

The static table maps SquashFS compression ids to compiled wrappers or unsupported placeholders. LZMA is explicitly unsupported; disabled algorithms appear as unsupported stubs with names for clear mount errors.

`get_comp_opts()` reads optional compressor-specific data after the superblock when the filesystem flag says options are present, then calls the selected wrapper’s `comp_opts`.

`squashfs_decompressor_setup()` combines compressor options with the selected threading implementation’s `create()` method to produce `msblk->stream`.
