# File Research: sources/os/linux/linux-stable/fs/cramfs/uncompress.c

This file wraps zlib inflate for CramFs block decompression.

Key responsibilities:
- Maintains a single static `z_stream`.
- Initializes and frees zlib workspace.
- Decompresses one compressed CramFs block into a destination buffer.

Important control flow:
- `cramfs_uncompress_init()` allocates the zlib workspace on the first user and increments `initialized`.
- `cramfs_uncompress_block()` resets the stream, inflates with `Z_FINISH`, and returns decompressed byte count.
- If reset fails, it reinitializes the stream.
- `cramfs_uncompress_exit()` decrements `initialized` and frees workspace when it reaches zero.

Dependencies:
- Uses Linux zlib inflate APIs.
- Called under the CramFs read mutex in `inode.c`.

Risks and invariants:
- Decompression is explicitly single-threaded due to the shared stream.
- Inflate failures are logged and returned as `-EIO`.
