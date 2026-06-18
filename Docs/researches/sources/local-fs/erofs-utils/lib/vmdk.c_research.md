# File Research: sources/local-fs/erofs-utils/lib/vmdk.c

## Scope

This file emits a VMware VMDK descriptor that describes the primary EROFS image and any extra devices as flat extents.

## Public And Internal APIs Covered

- `erofs_dump_vmdk_desc()` writes the full descriptor to a `FILE *`.
- Internal `erofs_vmdk_desc_add_extent()` writes one or more extent lines for a flat image, splitting large sector counts.

## Control Flow And Behavior

- The descriptor CID is derived by XORing four 32-bit words of the filesystem UUID; parent CID is fixed to `0xffffffff`.
- Primary-device block count and extra-device block counts are converted to 512-byte sectors using `blkszbits - 9`.
- Extent lines use `twoGbMaxExtentFlat` and `FLAT` extents. Each line is capped at `0x80000000 >> 9` sectors by the helper loop.
- Extra-device extent filenames prefer `src_path`; otherwise the device tag is used.
- The disk database reports hardware version `4`, IDE adapter type, 16 heads, 63 sectors, and cylinders rounded up from total sectors.

## State And Data Structures

- Reads `erofs_sb_info` UUID, device name, block size, primary-device block count, extra-device array, tags, paths, and block counts.

## Dependencies

- Standard formatted I/O and EROFS internal type/helpers such as `min_t()` and `DIV_ROUND_UP()`.

## Risks And Invariants

- This file assumes block size is at least 512 bytes so `blkszbits - 9` is valid.
- `fprintf()` failures from descriptor templates are not checked, while extent-line failures are converted to `-errno`.
- Device tags used as filenames must be meaningful and NUL-terminated enough for descriptor consumers.
