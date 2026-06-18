# File Research: sources/os/linux/linux/block/partitions/atari.h

Defines Atari root sector and partition entry wire layouts.

Key structures:
- `struct partition_info` contains flag byte, 3-byte partition ID, big-endian start sector, and big-endian size.
- `struct rootsector` contains boot-code padding, 8 ICD partition entries, disk size, 4 primary partition entries, bad-sector-list metadata, and checksum.

Research relevance:
- This header provides packed on-disk structures consumed by `atari.c`.
- The layout reflects both primary AHDI entries and ICD/Supra extended entries.
