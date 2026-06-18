# File Research: sources/os/linux/linux/block/partitions/acorn.c

Implements multiple Acorn/RISC OS partition table parsers, each conditional on its Kconfig subformat.

Supported formats:
- Cumana/ADFS chained style.
- Native ADFS/FileCore.
- RISCiX subpartition table.
- Linux partitions embedded in Acorn partition regions.
- ICS partition table with checksum.
- PowerTec SCSI partition table with checksum.
- EESOX SCSI partition table with XOR-obfuscated table.

Important functions:
- `adfs_partition()` validates an ADFS boot block and emits a partition from its disc record.
- `riscix_partition()` parses RISCiX records and subpartitions.
- `linux_partition()` parses Acorn Linux native/swap records.
- `adfspart_check_CUMANA()`, `adfspart_check_ADFS()`, `adfspart_check_ICS()`, `adfspart_check_POWERTEC()`, `adfspart_check_EESOX()` are the exported parser entry points declared in `check.h`.

Format notes:
- Several parsers read fixed sectors such as sector 6, sector 0, or sector 7.
- ICS uses a checksum seeded with `0x50617274`.
- PowerTec rejects PC/BIOS MBR-looking sectors before checksum validation.
- EESOX derives partition sizes from adjacent start addresses because the table lacks explicit sizes.
- RISCiX and Linux parsing may emit nested partition entries.

Research relevance:
- This file shows the partition layer’s legacy format support pattern: format probe, diagnostic text in `pp_buf`, and calls to `put_partition()`.
