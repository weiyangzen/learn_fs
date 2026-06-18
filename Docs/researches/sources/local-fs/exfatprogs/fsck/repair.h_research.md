# File Research: sources/local-fs/exfatprogs/fsck/repair.h

`repair.h` defines the repair problem-code namespace and public repair functions for `fsck.exfat`.

Problem codes are grouped by broad area:
- `ER_BS_*` for boot-sector/checksum/boot-region issues.
- `ER_DE_*` for directory entry set issues, including checksum, unknown/unused entries, file/stream/name fields, duplicated/invalid/dot names, upcase, and bitmap entries.
- `ER_FILE_*` for valid size, invalid clusters, first cluster, smaller/larger size mismatches, duplicate clusters, and zero-size no-FAT cases.
- `ER_VENDOR_GUID` for vendor extension GUID anomalies.
- `ER_MBR_*` for recursive MBR requirements and clearing.

It typedefs `er_problem_code_t` to `unsigned int`, forward-declares `struct exfat_fsck`, and declares:
- `exfat_repair_ask()` for generic repair prompts.
- `exfat_repair_rename_ask()` for filename-specific repairs that need dentry iterator and UTF-16 name mutation.
