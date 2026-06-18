# File Research: sources/local-fs/xfsprogs/mkfs/lts_6.1.conf

This mkfs profile captures v5 feature defaults for upstream Linux 6.1 LTS at its 2022 release timeframe.

Metadata enables bigtime, CRC, finobt, inobtcount, and reflink. It disables metadir, rmapbt, and autofsck. Sparse inodes are enabled. nrext64, exchange-range, and parent pointers remain disabled.

The feature set matches the 5.15-era modern default baseline while still omitting rmapbt and later namespace/extent-count defaults.
