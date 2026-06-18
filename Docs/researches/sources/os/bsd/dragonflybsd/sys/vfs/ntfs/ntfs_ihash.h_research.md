# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.h

This header exports the NTFS ntnode hash API and `ntfs_hashlock`.

Declarations include hash initialization/uninitialization, lookup, get, insert, and remove functions. `ntfs_nthashget()` is declared here but not implemented in the corresponding `ntfs_ihash.c`.

Research notes: consumers should verify whether `ntfs_nthashget()` is dead legacy API before using it.
