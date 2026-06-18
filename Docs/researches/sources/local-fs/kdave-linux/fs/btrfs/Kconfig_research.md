# File Research: sources/local-fs/kdave-linux/fs/btrfs/Kconfig

Purpose: Defines the kernel configuration surface for the Btrfs filesystem in this source tree.

Key options:
- `BTRFS_FS`: main tristate filesystem option. Selects block cgroup bio punt support, checksumming and compression libraries, iomap, RAID6/XOR helpers, xxhash, and depends on `PAGE_SIZE_LESS_THAN_256KB`.
- `BTRFS_FS_POSIX_ACL`: enables POSIX ACL support through `FS_POSIX_ACL`.
- `BTRFS_FS_RUN_SANITY_TESTS`: enables module-load regression tests for free space, extent maps, extent buffers, inodes, qgroups, chunk allocation, RAID stripe tree, delayed refs, and related subsystems.
- `BTRFS_DEBUG`: enables expensive runtime debugging, leak checks, debug sysfs, and optional forced fragmentation. Selects `REF_TRACKER` when stack traces are supported.
- `BTRFS_ASSERT`: enables runtime invariant assertions intended for developer/debug builds.
- `BTRFS_EXPERIMENTAL`: gates unstable features including COW fixup warning, mirror read policies, send stream v3 fs-verity, raid-stripe-tree, extent tree v2, large folio/block-size support, async data-write checksum generation, and remap-tree.

Dependencies and integration: This file controls objects added by `fs/btrfs/Makefile`, especially `acl.o`, `ref-verify.o`, tests, zoned support, and verity support. Experimental features affect conditional code paths elsewhere, including async checksum behavior in `bio.c`.

Risk notes: `BTRFS_EXPERIMENTAL` is a broad feature gate rather than one knob per feature, so enabling it can expose several unrelated unstable paths at once. `BTRFS_ASSERT` can intentionally panic on invariant failure.
