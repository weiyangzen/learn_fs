# File Research: sources/local-fs/exfatprogs/mkfs/mkfs.c

`mkfs.c` is the main implementation for `mkfs.exfat`. It parses formatting options, probes the target, optionally builds a GPT or MBR wrapper, computes exFAT layout geometry, discards/zeros target ranges, writes all filesystem metadata, verifies writes when requested, and rolls back GPT structures on failure.

Global state:
- `struct exfat_mkfs_info finfo` stores target offsets/lengths, FAT/cluster/bitmap/upcase/root layout, volume serial, and owned GPT buffers/regions.
- `fd_rnddev` caches `/dev/urandom` for GUID generation.

Option handling supports volume label/GUID, sector size, cluster size, boundary alignment, bitmap packing, custom upcase table, custom bootcode message, partition-table mode, full format, force overwrite, read-back verification, no-discard, quiet/verbose, version, and help. Existing filesystem/partition signatures are detected through libblkid; interactive terminals refuse overwrite unless `-F` is set.

Partition-table support:
- `build_gpt()` constructs protective MBR, main/backup GPT headers, and a 128-entry GPT partition-entry array. It enforces 1 MiB minimum alignment for GPT, checks device alignment offset, calculates usable/aligned bounds, assigns GUIDs, computes EFI CRC32 values, and transfers buffers into `finfo.gpt`.
- `exfat_setup_boot_sector()` embeds exFAT BPB/BSX fields and can place a recursive MBR partition entry when `PART_TABLE_MBR` is selected.
- GPT writes are performed before exFAT metadata, after endian conversion. On later failure, `exfat_zero_mkfs_data_regions()` and `exfat_write_mkfs_data_regions()` wipe the GPT regions.

Filesystem layout is computed by `exfat_build_mkfs_info()`. It sets target sector/byte region, validates cluster and boundary sizes, places the FAT after the 24-sector boot area rounded to boundary alignment, computes FAT length from maximum clusters, places the cluster heap, places allocation bitmap, optionally moves the bitmap with `exfat_pack_bitmap()`, then lays out upcase table and root directory clusters. It also computes the upcase checksum and generates a timestamp-derived volume serial.

Metadata writing sequence in `make_exfat()`:
1. Main volume boot record via `exfat_create_volume_boot_record()`.
2. Backup volume boot record.
3. FAT table via `exfat_create_fat_table()`.
4. Allocation bitmap via `exfat_create_bitmap()`.
5. Upcase table via `exfat_create_upcase_table()` from `upcase.c`.
6. Root directory entries via `exfat_create_root_dir()`.

Boot-record writing is split into:
- `exfat_write_boot_sector()` for the PBR and checksum update.
- `exfat_write_extended_boot_sectors()` for extended boot sectors with signatures.
- `exfat_write_oem_sector()` for OEM and reserved sectors.
- `exfat_create_volume_boot_record()` to write the checksum sector after the preceding sectors.

FAT and allocation data:
- `write_fat_entry()` writes individual FAT entries and mirrors them in a verification buffer when `-C` is used.
- `write_fat_entries()` creates linked cluster chains ending in `EXFAT_EOF_CLUSTER`.
- `exfat_create_fat_table()` writes reserved entries 0/1, then chains for bitmap, upcase table, and root directory, and records `finfo.used_clu_cnt`.
- `exfat_create_bitmap()` creates an allocation bitmap with bits set for the metadata clusters already consumed.

Root directory creation writes initial dentries:
- volume label dentry.
- volume GUID dentry if requested, otherwise a reserved invalid GUID slot.
- allocation bitmap dentry.
- upcase table dentry when upcase length is nonzero.

Upcase handling:
- `exfat_load_upcase()` defaults to the built-in default upcase table or loads a user-supplied binary file by `mmap()` or read fallback. It does not validate supplied table semantics, only size/empty conditions.
- `exfat_free_upcase()` dispatches to `munmap` or `free`.

Device preparation:
- `exfat_discard_dev()` issues block discard in 2 GiB chunks for block devices unless disabled.
- `exfat_zero_out_disk()` writes zeros to either the first `EXFAT_HEAD_ZERO_OUT` bytes for quick format or the full device for full format; optional verification rereads zeroed ranges.
- `check_existing_filesystem()` uses blkid to detect existing filesystem and partition table signatures.

Utility routines include `parse_size()` for K/M suffix parsing with overflow checks; random GUID helpers `exfat_open_rnddev()`, `exfat_close_rnddev()`, and `exfat_gen_guid()`; and GPT region write/verify helpers.

Notable implementation detail: the long option table declares `{"partition-table", no_argument, NULL, 'P'}` while the short option string uses `P:` and the handler expects `optarg`. The intended CLI documented by usage is `--partition-table=auto|none|mbr|gpt`; the table entry appears inconsistent with that intended behavior.
