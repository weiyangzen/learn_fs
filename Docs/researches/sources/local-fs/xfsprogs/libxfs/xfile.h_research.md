# File Research: sources/local-fs/xfsprogs/libxfs/xfile.h

## Role

`xfile.h` declares the memfd/tmpfile-backed scratch storage abstraction used by offline libxfs code.

## Interface

- `struct xfile_fcb` owns shared backing-file state: list node, fd, and refcount.
- `struct xfile` references an fcb and records its partition start and maximum writable bytes.
- `xfile_create` creates a private xfile when `maxbytes` is zero, or a bounded partition otherwise.
- `xfile_destroy` releases the partition/fcb.
- `xfile_load` and `xfile_store` read/write byte ranges relative to the xfile partition.
- `xfile_bytes` reports allocated backing bytes.
- `xfile_discard` punches out a byte range.

## Notable Assumptions

The header intentionally exposes a small byte-addressed API. Backing implementation choices, sharing policy, accounting, and fallback creation strategies live in `xfile.c`.
