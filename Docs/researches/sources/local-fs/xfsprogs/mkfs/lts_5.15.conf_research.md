# File Research: sources/local-fs/xfsprogs/mkfs/lts_5.15.conf

This mkfs profile captures v5 feature defaults for upstream Linux 5.15 LTS at its 2021 release timeframe.

Metadata enables bigtime, CRC, finobt, inobtcount, and reflink. It disables metadir, rmapbt, and autofsck. Inode settings keep sparse enabled and nrext64/exchange disabled. Naming keeps parent pointers disabled.

The profile marks the transition to bigtime and inode btree count defaults while keeping rmap, metadir, and parent pointer features off for compatibility.
