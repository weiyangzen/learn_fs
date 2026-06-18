# sources/test-tools/xfstests/tests/btrfs/259

## Purpose
Make sure btrfs defrag ioctl won't defrag compressed extents which are already at their max capacity. Btrfs uses 128K as max extent size for compressed extents, this would result several compressed extents all at their max size success, all done. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick defrag fiemap compress`. Requirement and capability gates: line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 15: `_require_scratch`; line 16: `_require_xfs_io_command "fiemap"`; line 18: `_scratch_mkfs >> $seqres.full`; line 20: `_scratch_mount -o compress`; line 24: `$XFS_IO_PROG -f -c "pwrite -S 0xee 0 16m" -c sync $SCRATCH_MNT/foobar >> $seqres.full`; line 27: `old_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`; line 30: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" >> $seqres.full`; line 31: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" > $tmp.before`; line 33: `$BTRFS_UTIL_PROG filesystem defrag "$SCRATCH_MNT/foobar" >> $seqres.full`; line 34: `sync`; line 36: `new_csum=$(_md5_checksum $SCRATCH_MNT/foobar)`; line 40: `$XFS_IO_PROG -c "fiemap -v" "$SCRATCH_MNT/foobar" > $tmp.after`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick defrag fiemap compress`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 259 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
