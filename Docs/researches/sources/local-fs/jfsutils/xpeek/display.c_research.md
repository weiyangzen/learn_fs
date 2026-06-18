# File Research: sources/local-fs/jfsutils/xpeek/display.c

Implements the generic `display` command for reading arbitrary aggregate blocks and rendering them as raw hex/ascii or selected JFS metadata structures.

Main entry point:
- `display(void)`: parses `block [offset [format [count]]]`, reads an aligned region, and dispatches by format.

Supported formats:
- `a`: byte/ascii hex dump; default length is one aggregate block.
- `x`: 4-byte unit hex-style dump through the same byte display routine; default count is `bsize / 4`.
- `i`: `struct dinode`; swaps with `ujfs_swap_dinode`, then calls `display_inode`.
- `I`: `struct iag`; swaps with `ujfs_swap_iag`, then calls `display_iag`.
- `s`: `struct superblock`; swaps with `ujfs_swap_superblock`, calls `display_super`, and writes back if changed.
- `X`: accepted in size calculation as `xad_t`, but falls through to “specified format not yet supported” in the final switch.

Hex rendering:
- `display_hex(char *addr, unsigned length, unsigned offset)` prints 16 bytes per line with offset, grouped hex text, and printable ASCII.
- Calls `more()` every 16 lines.

Integration points:
- Calls shared structure display functions implemented in `inode.c`, `iag.c`, and `super.c`.
- Uses globals `fp`, `bsize`, `l2bsize`, and `type_jfs`.
- Uses `ujfs_rw_diskblocks` for raw block access.

Notable behavior and risks:
- The `X` format is partially implemented only for sizing, not actual XAD rendering.
- `len` is rounded up to the aggregate block size, but allocation and read size are driven directly by user-controlled count and offset.
- If `display_super` changes a superblock, this command writes the whole read buffer back to the originally requested block address, making correct offset/block selection important.
