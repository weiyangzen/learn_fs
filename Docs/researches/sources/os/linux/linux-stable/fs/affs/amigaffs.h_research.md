# File Research: sources/os/linux/linux-stable/fs/affs/amigaffs.h

This header defines the AFFS on-disk constants and packed-ish layout structures used by the rest of the AFFS driver.

Major contents:
- Defines Amiga filesystem magic values for OFS, FFS, international, dircache, and MUFS variants.
- Defines AFFS primary and secondary block types: `T_SHORT`, `T_LIST`, `T_DATA`, `ST_ROOT`, `ST_USERDIR`, `ST_FILE`, `ST_SOFTLINK`, `ST_LINKFILE`, and `ST_LINKDIR`.
- Defines `AFFS_ROOT_BMAPS` as the number of bitmap pointers stored directly in the root block.
- Defines `AFFS_EPOCH_DELTA`, converting Amiga timestamps from the 1978-01-01 epoch to Unix time.

On-disk structure model:
- `struct affs_date` and `struct affs_short_date` describe Amiga date fields as days, minutes, and 1/50-second ticks.
- `struct affs_root_head` and `struct affs_root_tail` describe root block metadata, including bitmap block pointers, bitmap extension pointer, root/disk timestamps, disk name, dircache pointer, and root secondary type.
- `struct affs_head` and `struct affs_tail` describe normal file, directory, link, and extension block headers/tails.
- `struct slink_front` models a symlink header block whose payload is variable-length `symname`.
- `struct affs_data_head` models OFS data blocks, including sequence, size, next block, checksum, and data payload.

Permission definitions:
- The `FIBF_*` constants map Amiga protection bits to Linux mode handling.
- Owner bits are inverted for read/write/delete semantics where `NO*` bits mean denial.
- `FIBF_ARCHIVED` is intentionally cleared by Linux on writes.
- `FIBF_MASK` documents which protection bits Linux mutates.

Key dependencies:
- Used by AFFS helpers in `affs.h` and implementation files to address on-disk fields through endian-aware accessors.
- All multi-byte disk fields are big-endian types, so callers must use `be*_to_cpu()` and `cpu_to_be*()` conversions.
