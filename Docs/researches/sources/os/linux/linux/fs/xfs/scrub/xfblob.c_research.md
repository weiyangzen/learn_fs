# File Research: sources/os/linux/linux/fs/xfs/scrub/xfblob.c

This file implements `xfblob`, an append-only blob store backed by an `xfile`. It stores variable-length byte strings and returns xfile offsets as cookies for later retrieval/freeing.

Data format:
- Every blob is preceded by a packed `struct xb_key`:
  - `xb_magic`: `XB_KEY_MAGIC`
  - `xb_size`: blob payload size
  - `xb_offset`: byte offset of this key
- Blob data follows the key immediately.
- `last_offset` starts at `PAGE_SIZE`, leaving the first page unused/reserved.

Entry points:
- `xfblob_create`: creates backing xfile and initializes blob metadata.
- `xfblob_destroy`: destroys xfile and frees object.
- `xfblob_store`: writes key and payload, returns cookie, advances `last_offset`.
- `xfblob_load`: validates key magic/offset and loads payload into caller buffer.
- `xfblob_free`: validates key and discards key+payload range.
- `xfblob_bytes`: reports backing xfile usage.
- `xfblob_truncate`: discards all blobs after the first page and resets `last_offset`.

Error behavior:
- Invalid key magic or offset returns `-ENODATA` and asserts.
- Loading into too-small caller buffer returns `-EFBIG` and asserts.
- If payload store fails after key store succeeds, the key range is discarded.

Risk notes:
- Freed blobs are discarded but not reused; new stores always append at `last_offset`.
- Cookies are raw offsets and must come from this blob store.
- The implementation is simple variable-size storage for repair scratch data, not a general allocator.
