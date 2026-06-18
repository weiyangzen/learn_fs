# File Research: sources/virtualization/libblockdev/src/plugins/fs/f2fs.c

Implements F2FS support for libblockdev’s filesystem plugin.

Key entry points:
- `bd_fs_f2fs_is_tech_avail()` checks mode support and utility availability.
- `bd_fs_f2fs_mkfs()` runs `mkfs.f2fs`.
- `bd_fs_f2fs_check()` runs `fsck.f2fs --dry-run`.
- `bd_fs_f2fs_repair()` runs `fsck.f2fs -a`.
- `bd_fs_f2fs_get_info()` combines `dump.f2fs` parsing with common UUID/label probing.
- `bd_fs_f2fs_resize()` runs `resize.f2fs`, optionally in safe shrink mode.
- `bd_fs_f2fs_check_label()` enforces F2FS label length.

Core mechanics:
- Dependency checks include versioned checks for `fsck.f2fs >= 1.11.0` for check mode and `resize.f2fs >= 1.12.0` for safe shrink.
- `can_check_f2fs_version()` special-cases old tools whose version cannot be queried and reports them as too old.
- `bd_fs_f2fs_mkfs_options()` maps label, no-discard, and force to `mkfs.f2fs` options.
- `bd_fs_f2fs_get_info()` parses sector size, total filesystem sectors, and superblock feature bits from `dump.f2fs`.
- Resize refuses shrink without `safe=TRUE` because `resize.f2fs` may otherwise print an error but return success.

Important invariants:
- Setting label or UUID on an existing F2FS device is reported unsupported.
- F2FS resize sizes are in filesystem sectors, not bytes.
- Missing sector-size output is tolerated for `dump.f2fs` 1.15 by setting `sector_size` to 0.
- F2FS labels are capped at 512 characters.

Filesystem/block relevance:
- Provides F2FS creation, check/repair, metadata query, and resize support through the f2fs-tools command set.

Notable risks:
- Info parsing depends on exact `dump.f2fs` text prefixes.
- Safe shrink behavior depends on tool version detection.
- A zero sector size from older `dump.f2fs` output can prevent byte-to-sector conversion in generic resize paths.
