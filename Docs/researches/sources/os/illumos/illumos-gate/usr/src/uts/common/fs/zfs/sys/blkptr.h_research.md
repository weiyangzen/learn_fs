# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/blkptr.h

Read status: complete, 39 lines.

Purpose: declares helpers for embedded block pointer encoding and decoding.

Key APIs:
- `encode_embedded_bp_compressed()` writes compressed embedded data into a `blkptr_t`.
- `decode_embedded_bp_compressed()` extracts compressed embedded payload data.
- `decode_embedded_bp()` decodes an embedded block pointer into a caller buffer.

Dependencies: `spa.h` for `blkptr_t` and block pointer constants; `zio.h` for compression enum types.

Research notes:
- This is a narrow interface for embedded block pointer handling, used where small payloads are stored directly inside a block pointer instead of separate allocated blocks.
