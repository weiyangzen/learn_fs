# File Research: sources/teaching/xv6-public/memide.c

Memory-backed replacement for `ide.c`.

Key behavior:
- Uses linker-provided `_binary_fs_img_start` and `_binary_fs_img_size` as an in-memory disk image.
- `ideinit` records the memory disk pointer and block count.
- `ideintr` is a no-op.
- `iderw` copies block data between buffers and the embedded image, clearing `B_DIRTY` or setting `B_VALID`.

Role:
- Enables `kernelmemfs` builds that run without a scratch disk.
- Only accepts requests for device 1.
