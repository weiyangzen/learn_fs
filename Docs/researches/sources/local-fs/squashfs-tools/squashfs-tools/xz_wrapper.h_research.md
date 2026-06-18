# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.h

Private data structures and endian helpers for the XZ compressor wrapper.

Defines:
- Big-endian `SQUASHFS_INSWAP_COMP_OPTS()` for stored compressor options; no-op on little-endian builds.
- `MEMLIMIT` as 32 MiB for decompression.
- `struct bcj` for named BCJ filters and selection state.
- `struct filter` for a liblzma filter chain, scratch buffer, and compressed length.
- `struct xz_stream` for per-compressor stream state, selected filter list, dictionary size, and LZMA options.
- `struct comp_opts` containing on-disk XZ compressor options: dictionary size and BCJ flags.

Included by `xz_wrapper.c`; not a broad public API.
