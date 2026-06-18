# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.c

This file implements the in-core `ntnode` hash table for NTFS. It allocates a hash table sized via `vfs_inodehashsize()`, keyed by device minor plus inode number, and protects lookup/insert/remove with a DragonFly LWKT token. A separate exported `ntfs_hashlock` is used by higher-level allocation logic in `ntfs_ntlookup()`.

Functions: `ntfs_nthashinit()`, `ntfs_nthash_uninit()`, `ntfs_nthashlookup()`, `ntfs_nthashins()`, and `ntfs_nthashrem()`.

Dependencies: `ntfs.h`, `ntfs_inode.h`, `ntfs_ihash.h`.

Research notes: the header declares `ntfs_nthashget()`, but this implementation does not define it. Actual lookup users call `ntfs_nthashlookup()`.
