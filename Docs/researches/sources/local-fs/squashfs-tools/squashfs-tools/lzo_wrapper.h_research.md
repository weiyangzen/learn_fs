# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.h

Data definitions for LZO compressor support.

Defines:
- Big-endian swap macro for LZO compressor options.
- Algorithm IDs matching the `lzo[]` table order.
- Default compression level for `SQUASHFS_LZO1X_999`.
- `struct lzo_comp_opts` on-disk option layout.
- `struct lzo_algorithm` lookup entries.
- `struct lzo_stream` workspace/temp-buffer holder.
- `LZO_MAX_EXPANSION(size)` for safe temporary compression output sizing.
- Prototype for `lzo1x_999_wrapper()`.

Key role: connects LZO library APIs, option serialization, and SquashFS compressor vtable implementation.
