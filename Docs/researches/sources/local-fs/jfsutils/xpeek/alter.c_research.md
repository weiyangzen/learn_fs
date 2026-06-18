# File Research: sources/local-fs/jfsutils/xpeek/alter.c

Implements the `alter` command for `jfs_debugfs`, allowing direct byte-level modification of a block device by supplying a JFS aggregate block number, a hex offset within that block, and an even-length hex digit string.

Main entry point:
- `alter(void)`: parses arguments from the current `strtok` command stream or prompts interactively.
- Converts `block` to a byte address with `block << l2bsize`.
- Parses `offset` as hexadecimal.
- Validates that the supplied hex string has an even number of digits.
- Reads a block-aligned region from disk with `ujfs_rw_diskblocks(..., GET)`.
- Converts each pair of hex digits into a byte and writes it into the buffer at the requested offset.
- Writes the modified aligned region back with `ujfs_rw_diskblocks(..., PUT)`.

Integration points:
- Uses globals `fp`, `bsize`, and `l2bsize` from `xpeek.c`/`xpeek.h`.
- Uses libfs device I/O from `devices.h`.
- Exposed through the command dispatcher in `xpeek.c`.

Notable behavior and risks:
- This is a raw destructive editor with no structural validation of JFS metadata.
- Length rounding uses `offset + hex_length` where `hex_length` is digit count, not byte count, so it may read/write a larger aligned range than strictly necessary.
- No explicit bounds check ensures `offset + bytes_to_write` stays within the allocated block-aligned buffer if pathological offsets overflow unsigned arithmetic.
- Uses `strtoull`/`strtoul` errno checks but does not reset `errno` before parsing `offset`.
