# File Research: sources/local-fs/xfsprogs/mkfs/lts_4.19.conf

This mkfs profile captures v5 feature defaults corresponding to upstream Linux 4.19 LTS at its 2018 release timeframe.

Metadata enables CRC and finobt, disables bigtime, inobtcount, metadir, reflink, rmapbt, and autofsck. Inode settings enable sparse inodes and disable nrext64 and exchange-range. Naming disables parent pointers.

The resulting filesystem targets older LTS compatibility with conservative v5 metadata features and without reflink or modern namespace/extent-count features.
