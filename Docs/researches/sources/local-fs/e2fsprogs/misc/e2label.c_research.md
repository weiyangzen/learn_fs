# File Research: sources/local-fs/e2fsprogs/misc/e2label.c

## Purpose
Implements a minimal volume label reader/writer for ext2-style superblocks.

## Main Behaviors
- Opens the device directly with POSIX `open`.
- Seeks to byte offset 1024 and reads a local partial `struct ext2_super_block`.
- Validates magic `0xEF53`.
- With one argument, prints `s_volume_name`.
- With two arguments, writes a zero-padded/truncated 16-byte label and rewrites the same partial superblock area.

## Important Functions
- `open_e2fs`: open, seek, read, and magic validation.
- `print_label`: formats the fixed-size volume name safely.
- `change_label`: updates `s_volume_name`, warns on truncation, and writes the superblock structure back.
- `main`: two-argument print or three-argument change dispatch.

## Dependencies
- Direct POSIX I/O only; this implementation does not use ext2fs open helpers.
- `support/nls-enable.h` for translated messages.

## Notes and Edge Cases
- The file defines a local partial superblock layout containing only fields needed around magic and volume name.
- Writes back the whole local partial struct, not only the volume-name field.
- Label length limit is `VOLNAMSZ` 16.
