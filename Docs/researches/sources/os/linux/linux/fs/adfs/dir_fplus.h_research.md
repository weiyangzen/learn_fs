# File Research: sources/os/linux/linux/fs/adfs/dir_fplus.h

Defines on-disk structures and constants for ADFS F+ big directories.

Key behavior:
- Defines `ADFS_FPLUS_NAME_LEN` as 255.
- Defines big-directory start/end magic constants.
- Defines packed/aligned `struct adfs_bigdirheader` with version, size, entry count, names size, parent id, and variable directory name.
- Defines `struct adfs_bigdirentry` with load/exec/length/indaddr/attr plus name length and name pointer.
- Defines `struct adfs_bigdirtail` with end magic, sequence, reserved bytes, and check byte.

Important interactions:
- Consumed by `dir_fplus.c`.
- F+ support expands maximum exposed name length compared with F directories.
