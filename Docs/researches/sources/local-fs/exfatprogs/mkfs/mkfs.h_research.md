# File Research: sources/local-fs/exfatprogs/mkfs/mkfs.h

`mkfs.h` declares mkfs layout constants, GPT structures, global formatting state, and helper functions shared by `mkfs.c`, `upcase.c`, and `crc.c`.

Key constants:
- `MIN_NUM_SECTOR` minimum target size in sectors.
- `EXFAT_MAX_CLUSTER_SIZE` as 32 MiB.
- `EXFAT_HEAD_ZERO_OUT` quick-format zeroing length.
- GPT entry size/count/array size and 1 MiB minimum GPT partition alignment.

`struct exfat_mkfs_data_region` describes an offset, length, and backing buffer for GPT region writes/verification/wipe.

`struct exfat_mkfs_info` is the central geometry/result structure:
- target sector/byte offsets and lengths.
- cluster counts and used cluster count.
- FAT, cluster heap, bitmap, upcase table, and root directory offsets/lengths/start clusters.
- upcase checksum and volume serial.
- GPT-owned buffers for protective MBR, main/backup headers, entry array, and data regions.

The header defines packed GPT structs:
- `struct exfat_guid`.
- `struct exfat_gpt_header`.
- `struct exfat_gpt_entry_attrs`.
- `struct exfat_gpt_entry`.

It declares global `finfo`, `exfat_create_upcase_table()`, GPT print macro `exfat_print_gpt_header()`, GPT region helpers, `exfat_efi_crc32()`, and GUID entropy helpers.

The header has a minor guard oddity: it uses `#ifndef _MKFS_H` but does not visibly `#define _MKFS_H` before declarations, so repeated inclusion protection depends on external context or is incomplete in this file as read.
