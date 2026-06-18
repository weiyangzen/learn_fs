# File Research: sources/virtualization/libblockdev/src/plugins/fs/ext.c

Implements libblockdev filesystem plugin support for ext2, ext3, and ext4. The file is mostly a shared implementation with thin per-version wrappers.

Key entry points:
- `bd_fs_ext_is_tech_avail()` maps requested filesystem modes to required utilities: `mke2fs`, `e2fsck`, `tune2fs`, and `resize2fs`.
- `bd_fs_ext{2,3,4}_mkfs()` creates filesystems through `mke2fs -t extN`.
- `bd_fs_ext{2,3,4}_check()` runs `e2fsck -f -n`, optionally with `-C 1` progress output.
- `bd_fs_ext{2,3,4}_repair()` runs `e2fsck -f -p` or unsafe `-y`.
- `bd_fs_ext{2,3,4}_set_label()` and `_set_uuid()` use `tune2fs`.
- `bd_fs_ext{2,3,4}_get_info()` reads superblock data through libext2fs.
- `bd_fs_ext{2,3,4}_resize()` runs `resize2fs`.
- `bd_fs_ext{2,3,4}_get_min_size()` parses `resize2fs -P`.

Core mechanics:
- Shared helpers perform nearly all work, with ext2/ext3/ext4 wrappers reusing the same code paths.
- `extract_e2fsck_progress()` parses e2fsck progress lines with a cached `GRegex` and maps five e2fsck stages onto 0-100%.
- `ext_mkfs_options()` converts generic mkfs options into `mke2fs` arguments: label, UUID, dry run, no discard, force, plus caller-supplied extra args.
- `ext_get_info()` opens the filesystem with libext2fs flags including superblock-only and checksum-ignore behavior, then extracts label, UUID, state, block size, block count, and free block count.
- `ext_get_min_size()` multiplies the `resize2fs -P` minimum block count by the current filesystem block size.

Important invariants:
- Ext labels are capped at 16 characters.
- UUID format validation delegates to common `check_uuid()`.
- A `NULL` UUID for set-uuid means `tune2fs -U random`.
- Resize sizes are converted from bytes to 512-byte-sector syntax expected by `resize2fs`.
- e2fsck exit codes 1 and 2 are treated as successful repair outcomes; check exit code 4 means errors left uncorrected but not an execution failure.

Filesystem/block relevance:
- This file is the ext-family adapter between libblockdev’s stable API and the ext userspace toolchain plus libext2fs superblock access.

Notable risks:
- Progress parsing assumes e2fsck’s numeric `-C` output format.
- Minimum-size parsing depends on localized/string output beginning with `Estimated minimum size`.
- The generic dispatcher calls the ext4 wrappers for all ext2/ext3/ext4 runtime operations, relying on tool compatibility.
