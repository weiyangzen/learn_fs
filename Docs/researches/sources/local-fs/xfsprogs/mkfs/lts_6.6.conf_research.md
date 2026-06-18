# File Research: sources/local-fs/xfsprogs/mkfs/lts_6.6.conf

This mkfs profile captures v5 feature defaults for upstream Linux 6.6 LTS at its 2023 release timeframe.

Metadata enables bigtime, CRC, finobt, inobtcount, reflink, and rmapbt. It disables metadir and autofsck. Inode settings enable sparse and nrext64 but disable exchange-range. Naming disables parent pointers.

This profile is the first LTS profile in the listed set with rmapbt and nrext64 enabled by default, while still keeping newer namespace features disabled.
