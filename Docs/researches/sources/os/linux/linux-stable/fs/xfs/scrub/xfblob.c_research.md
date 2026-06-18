# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/xfblob.c

Implements append-style variable-length blob storage over an `xfile`.

Core model:
- Each blob is stored as an `xb_key` header followed by payload bytes.
- The header records a magic value, blob size, and its own byte offset.
- The byte offset is returned as an opaque `xfblob_cookie` for later retrieval/free.

Key behavior:
- `xfblob_create` creates the backing xfile and starts blob allocation at `PAGE_SIZE`.
- `xfblob_load` validates the key magic and offset, verifies the caller buffer is large enough, then loads payload bytes.
- `xfblob_store` writes the key and payload, returns the old `last_offset` as the cookie, and advances `last_offset`; on payload write failure it discards the written key.
- `xfblob_free` validates the key and discards the key-plus-payload range.
- `xfblob_bytes` reports xfile memory consumption.
- `xfblob_truncate` discards all blob storage beyond the first page and resets `last_offset`.

Important constraints:
- Freed blob space is discarded but not reused by the allocator; storage is append-oriented.
- Invalid cookies trigger assertions and return `-ENODATA`.
