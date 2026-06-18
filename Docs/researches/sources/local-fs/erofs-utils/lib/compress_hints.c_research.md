# File Research: sources/local-fs/erofs-utils/lib/compress_hints.c

## Purpose
Loads and applies path-based compression hints for mkfs/import compression decisions.

## Main Data
- `compress_hints_head`: list of compiled regex hints.
- Each hint records physical cluster block count and compressor configuration index.

## Important Functions
- `erofs_load_compress_hints()`: parses the configured hints file, validates pcluster sizes and compressor config indexes, compiles patterns, and updates max pcluster blocks if needed.
- `z_erofs_apply_compress_hints()`: matches an inode source path and sets `inode->z_physical_clusterblks` and `inode->z_algorithmtype[0]`.
- `erofs_cleanup_compress_hints()`: frees hint entries.

## Behavior
- Hint file lines accept pcluster size, optional compressor config id, and regex/path pattern.
- Pcluster size `0` means the matched file should not be compressed.
- Invalid regex emits a detailed regex error.

## Interactions
- Called by `compress.c` when choosing pcluster size if `cfg.c_compress_hints_file` is set.
- Uses `erofs_fspath()` so hints match paths relative to the configured root.

## Notes
The `algorithmtype` field is a compressor configuration index here, not directly the on-disk algorithm id.
