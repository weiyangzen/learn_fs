# File Research: sources/os/linux/linux/fs/udf/Kconfig

## Purpose
Defines the kernel configuration option for UDF filesystem support.

## Main Contents
- `config UDF_FS`: tristate option named “UDF file system support”.
- Selects required infrastructure: `BUFFER_HEAD`, `CRC_ITU_T`, `NLS`, `LEGACY_DIRECT_IO`.
- Help text describes UDF use on CD-ROM/DVD, packet-written CDRW, and removable USB disks, with documentation pointer to `Documentation/filesystems/udf.rst`.

## Cross-File Relationships
- Controls compilation of the UDF module through `fs/udf/Makefile`.
- Selected dependencies match code usage in files such as `directory.c`/`inode.c` for CRC and buffer-head based block I/O.

## Risks / Review Notes
- No tunable sub-options are defined here; all feature variation is runtime mount/volume dependent or controlled by broader kernel config.
