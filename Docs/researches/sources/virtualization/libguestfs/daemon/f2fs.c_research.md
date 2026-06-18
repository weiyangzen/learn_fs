# File Research: sources/virtualization/libguestfs/daemon/f2fs.c

Implements minimal f2fs expansion support.

Key points:
- Optional group availability checks for `resize.f2fs`.
- `do_f2fs_expand` runs `resize.f2fs <device>`.
- Uses `COMMAND_FLAG_FOLD_STDOUT_ON_STDERR` because tool output/error behavior is command-oriented.
