# File Research: sources/local-fs/f2fs-tools/include/f2fs_fs.h

Central shared userspace F2FS header: on-disk format definitions, configuration state, feature table, endian helpers, block-layout math, and public helper prototypes.

Major areas:
- Platform setup: Android config inclusion, tool feature gates (`WITH_DUMP`, `WITH_DEFRAG`, `WITH_RESIZE`, `WITH_SLOAD`, etc.), Linux type fallbacks, write-life hint fallback, SELinux include gates.
- Core integer typedefs and endian conversion macros for little-endian F2FS disk structures.
- Debug/logging/assertion macros used across tools.
- Global constants: magic, block/sector sizing, checkpoint pack count, path/device limits, version lengths, curseg types, feature bits, file flags, checkpoint flags, inode inline flags, fault injection types.
- `struct f2fs_configuration`, the global `c`, centralizes mkfs/fsck/dump/sload/resize parameters, device information, feature toggles, compression configuration, current segment offsets, cached summaries, NAT/SIT journals, fault injection state, and zoned-device settings.
- Disk format structures: `f2fs_super_block`, `f2fs_checkpoint`, orphan block footer, inode, node footer, NAT entry/block, SIT entry/block, summary/journal structures, dentry block layout, device list entries.
- Layout macros: address counts per inode/direct/indirect node, dentry slot math, summary block layout, checkpoint bitmap offsets, SIT/NAT sizing, block/segment/zone alignment.
- Helper macros `set_sb()`, `get_sb()`, `set_cp()`, `get_cp()` hide endian conversion for global `sb`/`cp`.
- Inline helpers for extra inode size, inline xattr address count, reserved/overprovision calculation, checkpoint CRC folding, quota inode checks, feature parsing, root owner parsing, inode initialization, and structure-size runtime checks.
- Zoned block-device compatibility structs and helpers for older/newer Linux zone-report formats.

Important design notes:
- Many on-disk structs deliberately use zero-length arrays and comments warning not to use `sizeof` for block-sized objects because their usable layout depends on `F2FS_BLKSIZE`.
- `static_assert` guards fixed ABI sizes such as superblock, checkpoint header, node footer, NAT entry, SIT entry, summary entry, and directory entry.
- The feature table defines user-settable mkfs feature names, including `encrypt`, `extra_attr`, `quota`, `casefold`, `compression`, `ro`, and `packed_ssa`; some internal features such as `blkzoned` and `device_alias` are not directly settable.
- `check_block_struct_sizes()` is a runtime assertion suite for configurable block sizes and packed SSA.

Notable issue:
- On little-endian builds, `be32_to_cpu(x)` is defined using `__builtin_bswap64(x)`, which is suspicious for a 32-bit big-endian conversion. Any caller expecting a 32-bit swap may get incorrect widening/truncation behavior.
