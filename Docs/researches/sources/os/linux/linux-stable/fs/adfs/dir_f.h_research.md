# File Research: sources/os/linux/linux-stable/fs/adfs/dir_f.h
- Purpose: Defines on-disk structures for classic ADFS F-format directories.
- Main structures: `adfs_dirheader`, `adfs_direntry`, `adfs_olddirtail`, and `adfs_newdirtail`.
- Constants: Defines directory size, entry count, and short F-format filename limit.
- Integration: Consumed by `dir_f.c`, `dir.c`, and mount code that creates root object metadata.
- Research notes: Structures are direct on-disk layouts and should be treated as format contracts.
