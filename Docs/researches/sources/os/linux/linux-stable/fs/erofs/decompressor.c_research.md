# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor.c

## Summary
Implements the core compressed-data decompressor registry plus LZ4 and plain transform modes.

## Main Responsibilities
- Loads LZ4 compression configuration.
- Prepares sparse output pages for LZ4.
- Handles overlap and in-place decompression cases.
- Fixes compressed input size by skipping zero padding.
- Implements shifted/interlaced plain transforms.
- Parses compression configuration records.
- Initializes/exits registered decompressors.

## Key APIs
- `z_erofs_fixup_insize()`
- `z_erofs_stream_switch_bufs()`
- `z_erofs_parse_cfgs()`
- `z_erofs_init_decompressor()`
- `z_erofs_exit_decompressor()`

## Important Behavior
The LZ4 path can decompress directly, vm-map multi-page inputs/outputs, use global bounce buffers, or perform true in-place decompression when page overlap and margins allow.

## Risks
In-place decompression is highly sensitive to page ordering, margins, and overlap detection. Unsupported configured algorithms fail mount with `-EOPNOTSUPP`.
