# sources/test-tools/xfstests/tests/btrfs/299

## Purpose
Given a file with extents: [0 : 4096) (inline) [4096 : N] (prealloc) if a user uses the ioctl BTRFS_IOC_LOGICAL_INO[_V2] asking for the file of the non-inline extent, it results in reading the offset field of the inline extent, which is meaningless (it is full of user data..). If we are particularly lucky, it can be past the end of the extent buffer, resulting in a crash. This test creates that circumstance and asserts that logical inode resolution is still successful. In this subset it primarily covers logical-to-inode extent resolution.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick preallocrw logical_resolve`. Requirement and capability gates: line 20: `_require_scratch`; line 21: `_require_xfs_io_command "falloc" "-k"`; line 22: `_require_btrfs_command inspect-internal logical-resolve`; line 25: `_require_btrfs_no_nodatacow`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 20: `_require_scratch`; line 21: `_require_xfs_io_command "falloc" "-k"`; line 22: `_require_btrfs_command inspect-internal logical-resolve`; line 25: `_require_btrfs_no_nodatacow`; line 44: `_scratch_mkfs "--nodesize 64k" >> $seqres.full || _fail "mkfs failed"`; line 45: `_scratch_mount`; line 51: `$XFS_IO_PROG -fc "pwrite -q 0 1024" $f.inl.$i`; line 55: `$XFS_IO_PROG -fc "pwrite -q 0 1" $f.inl-var.$i`; line 58: `$XFS_IO_PROG -fc "falloc -k 0 1m" $f.evil`; line 59: `$XFS_IO_PROG -fc fsync $f.evil`; line 64: `$XFS_IO_PROG -fc "pwrite -q 0 1024" $f.inl.2.$i`; line 69: `logical=$(_btrfs_get_file_extent_item_bytenr $f.evil 0)`; line 75: `$XFS_IO_PROG -fc "pwrite -q 0 23" $f.evil`; line 81: `sync`. It documents fixed kernel commit context at line 26: `_fixed_by_kernel_commit 560840afc3e6 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick preallocrw logical_resolve`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through xfs_io. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 299 | Silence is golden`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
