# File Research: sources/os/linux/linux/fs/adfs/Makefile

Defines the ADFS module object composition.

Key behavior:
- Builds `adfs.o` when `CONFIG_ADFS_FS` is enabled.
- Combines:
  - `dir.o`
  - `dir_f.o`
  - `dir_fplus.o`
  - `file.o`
  - `inode.o`
  - `map.o`
  - `super.o`

Important interactions:
- Separates common directory handling from F and F+ format-specific directory implementations.
