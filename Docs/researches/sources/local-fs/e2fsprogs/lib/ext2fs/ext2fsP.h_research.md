# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2fsP.h

## Purpose
Private internal header for libext2fs implementation files.

## Key Definitions
- Includes `ext2fs.h` and optional `sys/stat.h`.
- `EXT2FS_MAX_NESTED_LINKS`.
- `ext2fsP_is_disk_device`: platform-specific block/character device test.
- `ext2fsP_get_time`: respects fake filesystem time.
- Internal badblocks/u32 list and iterator structs.
- Internal directory block list struct.
- `dir_context` for directory iteration callbacks.
- Inode cache structs.
- NLS table and operation callbacks.
- Progress meter structs and progress operation callbacks.

## Internal Prototypes
Declares helpers for:
- Directory block processing.
- Inline data EA removal/expansion/iteration.
- Numeric progress display.
- 64-bit bitmap backend operations.
- Memory-zero checks.
- File block offset limit checking.
- atexit callback registration/removal.

## Integration
Included by implementation files such as `ext_attr.c` and `extent.c`. It exposes implementation-only representations hidden from public consumers.

## Risks and Notes
- Changes can affect many libext2fs modules but are not intended as public API.
- `ext2fsP_get_time` is relevant for reproducible/fake-time tests.
