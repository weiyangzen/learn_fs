# File Research: sources/local-fs/jfsutils/xpeek/super.c

Implements display and modification of the standard JFS primary or secondary aggregate superblock.

Main command:
- `superblock(void)`: accepts optional `p` or `s`, reads the selected superblock with `ujfs_get_superblk`, calls `display_super`, and writes back with `ujfs_put_superblk` if changed.

Display/edit:
- `display_super(struct superblock *)`: prints superblock fields including:
  - magic/version/size/block sizes,
  - aggregate size,
  - platform and feature flags,
  - state,
  - compression,
  - secondary aggregate inode table PXD (`s_ait2`),
  - log device/serial/log PXD,
  - fsck workspace PXD,
  - timestamp,
  - fpack,
  - UUID, label, and log UUID for current JFS version.
- Converts state and flags into readable labels.
- Supports field-by-field modification through `m_parse`.
- Validates UUID fields using `uuid_parse`.

Integration points:
- Used directly by `superblock` command and indirectly by `display.c` format `s`.
- Uses `jfs_byteorder.h` conversion helpers for 24-bit/32-bit PXD fields.
- Uses PXD address macros from JFS headers.

Notable behavior and risks:
- This editor can alter core superblock identity, geometry, log, and fsck pointers with minimal validation.
- Endian conversion for fields uses byteorder macros inline for some PXD subfields; care is needed when comparing this to other code paths that swap whole superblocks.
- Argument handling has an `else if (strtok(...))` attached to the no-argument branch, so “too many arguments” after a valid first argument is not checked.
