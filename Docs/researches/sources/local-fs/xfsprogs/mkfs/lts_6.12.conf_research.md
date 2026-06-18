# File Research: sources/local-fs/xfsprogs/mkfs/lts_6.12.conf

This mkfs profile captures v5 feature defaults for upstream Linux 6.12 LTS at its 2024 release timeframe.

Metadata enables bigtime, CRC, finobt, inobtcount, reflink, and rmapbt. It disables metadir and autofsck. Inode settings enable sparse inodes and nrext64, while exchange-range remains disabled. Naming keeps parent pointers disabled.

Compared with 6.6, it keeps rmapbt and nrext64 on and still avoids exchange-range and parent pointers, making it a compatibility profile just before those later defaults in the 6.18 profile.
