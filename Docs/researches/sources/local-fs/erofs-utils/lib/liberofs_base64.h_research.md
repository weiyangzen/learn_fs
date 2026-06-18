# File Research: sources/local-fs/erofs-utils/lib/liberofs_base64.h

This small internal header declares base64 helpers:
- `erofs_base64_encode(const u8 *src, int srclen, char *dst)`
- `erofs_base64_decode(const char *src, int len, u8 *dst)`

It includes `erofs/defs.h` for `u8` and uses a normal include guard.

Known users in this group:
- OCI username/password encoding and decoding.
- Docker config auth field decoding.

The header does not define ownership or output sizing rules; callers must allocate sufficient destination buffers. In observed users, encode size is computed as `4 * DIV_ROUND_UP(input_len, 3)` and decode buffers are sized from encoded length.
