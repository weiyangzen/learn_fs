# File Research: sources/local-fs/xfsprogs/libxfs/xfblob.h

## Role

`xfblob.h` declares the cookie-addressed blob storage wrapper used by xfsprogs code that needs temporary variable-sized object storage over an `xfile`.

## Interface

- `struct xfblob` contains the backing `struct xfile` and next append offset.
- `xfblob_cookie` is a `loff_t` offset cookie.
- `xfblob_create` and `xfblob_destroy` manage the blob store.
- `xfblob_store` appends a blob and returns its cookie.
- `xfblob_load` retrieves a blob into a caller buffer.
- `xfblob_free` discards one stored blob range.
- `xfblob_truncate` discards all blob ranges and resets append state.

## Notable Assumptions

The header exposes no iterator or reuse mechanism. Allocation, validation, free-space punching, and append offset management are implemented in `xfblob.c`.
