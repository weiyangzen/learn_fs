# File Research: sources/os/linux/linux/fs/squashfs/decompressor_single.c

Implements the traditional single-stream decompression mode.

The stream contains one compressor-specific state object and one mutex. All decompression serializes through that mutex.

This is the lowest memory/concurrency option and reports max decompressors as `1`.
