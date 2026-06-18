# File Research: sources/virtualization/qemu/block/cloop.c

Implements QEMU's read-only CLOOP image format driver. It probes for the CLOOP shell-script magic, opens a file child, parses the 128-byte header area, reads big-endian block size and block count, validates block size, validates and loads the compressed-block offset table, allocates compressed/uncompressed buffers, and initializes a zlib stream.

Runtime reads are sector-aligned only. `cloop_co_preadv()` serializes access with a coroutine mutex, maps each requested sector to a compressed block, calls `cloop_read_block()` to lazily decompress the current block if needed, and copies 512-byte sectors into the caller qiov. Only one decompressed block is cached (`current_block`).

Important safety checks include: block size must be nonzero, 512-byte aligned, and <= 64 MiB; `n_blocks` and offset table sizing are bounded; offsets must be monotonic; compressed block size is capped at twice `MAX_BLOCK_SIZE`. The driver registers as format `cloop`, exposes `.bdrv_co_preadv`, default child permissions, 512-byte request alignment, and no write path.
