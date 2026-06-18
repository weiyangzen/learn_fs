# File Research: sources/local-fs/xfsprogs/libxfs/xfblob.c

## Role

`xfblob.c` implements append-only blob storage on top of `xfile`. It stores each blob behind a small metadata key and returns the byte offset as an opaque cookie for later load/free operations.

## Major Responsibilities

- Create a blob store backed by an unlimited private `xfile`.
- Store blobs by appending an `xb_key` header followed by payload bytes.
- Return the header offset as `xfblob_cookie`.
- Load blobs by validating the magic value and stored offset, then reading the payload.
- Free individual blobs by punching out their header and payload range.
- Truncate all blobs by discarding from `PAGE_SIZE` to the last appended offset and resetting append position.

## Storage Format

Each blob starts with packed `struct xb_key`: `xb_magic`, `xb_size`, and `xb_offset`. The magic constant is `XB_KEY_MAGIC`. `xfblob_create` initializes `last_offset` to `PAGE_SIZE`, leaving the first page unused; all blob offsets advance monotonically by header size plus payload size.

## Error Handling

`xfblob_load` and `xfblob_free` validate that the header magic matches and that `xb_offset` equals the supplied cookie. Bad cookies assert and return `-ENODATA`; an undersized load buffer asserts and returns `-EFBIG`. If payload store fails after the header write, the header range is discarded before returning the error.

## Notable Assumptions

- Cookies are trusted offsets into the xfile but still checked against the stored header.
- Freed blobs are not reused; only storage backing is discarded.
- `xfblob_truncate` assumes `last_offset` is at or beyond `PAGE_SIZE`.
