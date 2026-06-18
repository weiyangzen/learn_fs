# File Research: sources/local-fs/squashfs-tools/squashfs-tools/compressor.c

Compressor registry and help display implementation.

Behavior:
- Creates stub compressor records for algorithms not compiled in, and imports real `*_comp_ops` records for enabled algorithms.
- Maintains ordered global `compressor[]`: gzip, lzo, lz4, xz, zstd, lzma, unknown.
- `lookup_compressor(name)` and `lookup_compressor_id(id)` return matching records or the unknown sentinel.
- `valid_compressor()` checks whether a named compressor is supported in this build.
- `display_compressor_usage()` prints available compressors and compressor-specific option help.
- `print_selected_comp_options()` and `print_comp_options()` print one compressor’s options or all options.

Key role: runtime bridge between CLI parsing/help and compressor wrapper vtables.
