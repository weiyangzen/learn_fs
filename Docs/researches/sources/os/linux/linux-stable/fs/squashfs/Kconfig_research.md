# File Research: sources/os/linux/linux-stable/fs/squashfs/Kconfig

## Summary
Defines build-time and mount-time configuration for the Linux Squashfs 4.0 read-only compressed filesystem driver.

## Main Responsibilities
- Enables `CONFIG_SQUASHFS` as a block-device filesystem.
- Selects the file data read strategy: intermediate buffer cache or direct page-cache decompression.
- Selects decompressor threading mode: single, dynamically allocated multi-stream, percpu, or mount-time choice.
- Optionally enables the `threads=` mount parameter and compressed-block page-cache caching.
- Enables optional xattrs and compression backends: zlib, lz4, lzo, xz, and zstd.
- Controls default device block size and fragment-cache size for embedded systems.

## Important Behavior
`SQUASHFS_CHOICE_DECOMP_BY_MOUNT` compiles all three decompressor thread implementations and makes `threads=` accept mode names. Without it, a compile-time choice selects one implementation, while `SQUASHFS_MOUNT_DECOMP_THREADS` can still allow numeric thread counts for the multi decompressor.

`SQUASHFS_FILE_CACHE` builds the path that decompresses into an intermediate cache entry before copying to the page cache. `SQUASHFS_FILE_DIRECT` builds the path that decompresses directly into page-cache pages.

## Risks
The options are tightly coupled to the Makefile and `super.c` mount parsing. Invalid combinations would leave missing symbols for selected read or decompressor paths, so the `select` relationships are part of the functional contract.
