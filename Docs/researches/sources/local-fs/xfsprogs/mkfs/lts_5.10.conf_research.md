# File Research: sources/local-fs/xfsprogs/mkfs/lts_5.10.conf

This mkfs profile captures v5 feature defaults for upstream Linux 5.10 LTS at its 2020 release timeframe.

Compared with 4.19, it enables reflink while keeping bigtime, inobtcount, metadir, rmapbt, and autofsck disabled. Sparse inodes remain enabled. nrext64, exchange-range, and parent pointers remain disabled.

The profile represents the era where reflink became a default feature while later inode count, rmap, exchange, and parent pointer defaults were still off.
