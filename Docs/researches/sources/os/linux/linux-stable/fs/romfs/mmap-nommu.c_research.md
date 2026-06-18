# File Research: sources/os/linux/linux-stable/fs/romfs/mmap-nommu.c

NOMMU mmap support for ROMFS files stored directly on MTD devices.

Key responsibilities:
- `romfs_get_unmapped_area()` validates requested shared mapping bounds against file size and MTD size, adds the ROMFS file data offset, and delegates address selection to `mtd_get_unmapped_area()`.
- Converts unsupported MTD direct mapping from `-EOPNOTSUPP` to `-ENOSYS`.
- `romfs_mmap_prepare()` permits only NOMMU shared mappings.
- `romfs_mmap_capabilities()` returns MTD mmap capabilities when an MTD device exists, otherwise `NOMMU_MAP_COPY`.
- Defines read-only file operations using generic read/splice plus NOMMU mmap hooks.

Notable invariants:
- Direct mappings are only attempted for MTD-backed ROMFS.
- Nonzero requested addresses, out-of-file ranges, and out-of-MTD ranges are rejected.
- Private mappings are not supported by this direct NOMMU path.
