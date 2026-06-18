## sources/test-tools/xfstests/common/f2fs

Purpose: this library provides f2fs-specific requirement checks and fsck integration for the generic fstests harness.

Important APIs: `_require_scratch_f2fs_compression [algorithm]` verifies scratch availability, kernel compression feature exposure at `/sys/fs/f2fs/features/compression`, mkfs support for `-O compression,extra_attr`, and optionally mount support for `compress_algorithm=<algorithm>`. `_check_f2fs_filesystem device` unmounts or remounts the device read-only, runs `fsck.f2fs --dry-run`, logs failures to `$seqres.full`, restores the mount when appropriate, and returns success/failure. `_require_inject_f2fs_command metaarea member` validates `inject.f2fs` availability and that a specific meta area/member appears in the command help.

Control flow: compression probing is prerequisite oriented: check kernel feature, try mkfs, optionally try mount and immediately unmount. The fsck helper mirrors `common/rc` generic checking: detect mounted f2fs, transition it to a checkable state, run dry-run fsck into `$tmp.fsck.f2fs`, record diagnostics, and remount read-write if the filesystem was originally mounted and fsck passed.

State and persistence: no persistent state is created except temporary `$tmp.fsck.f2fs` and appended diagnostics in `$seqres.full`. It may reformat scratch during compression probing. It mutates mount state only through shared rc helpers.

Dependencies and integration: it expects `common/rc` globals and helpers such as `_require_scratch`, `_scratch_mkfs`, `_scratch_mount`, `_scratch_unmount`, `_fs_type`, `_umount_or_remount_ro`, `_mount_or_remount_rw`, `_mount`, `_log_err`, `_require_command`, `_notrun`, and `_exit`. It depends on `$F2FS_FSCK_PROG` and `$F2FS_INJECT_PROG`.

Risks: `_require_inject_f2fs_command` uses implicit globals `metaarea`, `member`, and `val` rather than local variables, which can leak into caller scope. `ssa`, `node`, and `dent` do not initialize `val`, so the constructed help invocation depends on shell state or empty expansion. Compression probing formats scratch, so callers must not expect existing scratch contents to survive.

Test signals: passing checks are silent or return zero. Failure evidence is a notrun reason for unsupported compression/injection features or `*** fsck.f2fs output ***` in `$seqres.full` when the filesystem is inconsistent.
