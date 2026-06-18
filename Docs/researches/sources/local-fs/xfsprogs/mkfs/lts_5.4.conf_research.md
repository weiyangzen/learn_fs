# File Research: sources/local-fs/xfsprogs/mkfs/lts_5.4.conf

This mkfs profile captures v5 feature defaults for upstream Linux 5.4 LTS at its 2019 release timeframe.

Metadata enables CRC, finobt, and reflink, while disabling bigtime, inobtcount, metadir, rmapbt, and autofsck. Sparse inodes are enabled. nrext64, exchange-range, and parent pointers are disabled.

The profile is essentially the 5.x reflink-era compatibility baseline before bigtime and inobtcount became defaults.
