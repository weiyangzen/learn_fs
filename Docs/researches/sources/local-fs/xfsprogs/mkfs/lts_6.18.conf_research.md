# File Research: sources/local-fs/xfsprogs/mkfs/lts_6.18.conf

This mkfs profile captures v5 feature defaults for upstream Linux 6.18 LTS at its 2025 release timeframe.

Metadata enables bigtime, CRC, finobt, inobtcount, reflink, and rmapbt, while metadir remains disabled. Unlike earlier LTS profiles in this group, there is no `autofsck` entry. Inode settings enable sparse, nrext64, and exchange-range. Naming enables parent pointers.

This is the most feature-forward LTS profile in the group, adding exchange-range and parent pointers to the 6.12-style baseline.
