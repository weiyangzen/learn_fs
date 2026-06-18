# File Research: sources/os/linux/linux/fs/adfs/dir_f.h

Defines on-disk structures for ADFS E/F directory format.

Key behavior:
- Defines `struct adfs_dirheader` with start sequence and start name.
- Defines fixed constants:
  - `ADFS_NEWDIR_SIZE` = 2048 bytes.
  - `ADFS_NUM_DIR_ENTRIES` = 77.
  - `ADFS_F_NAME_LEN` = 10.
- Defines packed `struct adfs_direntry` with name, load/exec/length, indirect address, and attributes.
- Defines old and new directory tail layouts with parent id, title/name fields, end sequence/name, and check byte.

Important interactions:
- Consumed by `dir_f.c` and `super.c`.
- `ADFS_NEWDIR_SIZE` is also used for the default root directory object size.
