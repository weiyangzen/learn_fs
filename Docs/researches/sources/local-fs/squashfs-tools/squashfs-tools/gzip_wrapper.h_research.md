# File Research: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.h

Data definitions for gzip compressor options and zlib strategy state.

Defines:
- Big-endian swap macro `SQUASHFS_INSWAP_COMP_OPTS`.
- Defaults: `GZIP_DEFAULT_COMPRESSION_LEVEL` and `GZIP_DEFAULT_WINDOW_SIZE`.
- `struct gzip_comp_opts` stored in SquashFS compressor options.
- `struct strategy` for option parsing.
- `struct gzip_strategy` for per-strategy compression attempts.
- `struct gzip_stream` containing a `z_stream` and flexible strategy array.

Key role: shared layout for gzip wrapper implementation and on-disk option serialization.
