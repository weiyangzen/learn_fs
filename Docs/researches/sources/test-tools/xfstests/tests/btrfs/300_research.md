# sources/test-tools/xfstests/tests/btrfs/300

## Purpose
Validate that snapshots taken while in a remapped namespace preserve the permissions of the user. _user_do executes each command as $qa_user in its own subshell. unshare sets the namespace for the running shell. The test must run in one user subshell to preserve the namespace over multiple commands. In this subset it primarily covers subvolume and snapshot metadata.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick subvol snapshot`. Requirement and capability gates: line 18: `_require_test`; line 19: `_require_user`; line 20: `_require_group`; line 21: `_require_unix_perm_checking`; line 22: `_require_unshare --keep-caps --map-auto --map-root-user`. Local helper surface: `cleanup()` (line 25). Important command/API calls include line 12: `_begin_fstest auto quick subvol snapshot`; line 15: `_fixed_by_kernel_commit 94628ad94408 "btrfs: copy dir permission and time when creating a stub subvolume"`; line 18: `_require_test`; line 19: `_require_user`; line 20: `_require_group`; line 21: `_require_unix_perm_checking`; line 22: `_require_unshare --keep-caps --map-auto --map-root-user`; line 26: `rm -rf $test_dir`; line 28: `rm -rf $tmp.*`; line 32: `mkdir $test_dir`; line 41: `unshare --user --keep-caps --map-auto --map-root-user;`; line 42: `$BTRFS_UTIL_PROG subvolume create subvol;`; line 43: `touch subvol/{1,2,3};`; line 44: `$BTRFS_UTIL_PROG subvolume create subvol/subsubvol;`. It documents fixed kernel commit context at line 15: `_fixed_by_kernel_commit 94628ad94408 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick subvol snapshot`, install cleanup if needed, enforce requirements, then creates or deletes subvolumes/snapshots, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Snapshot and subvolume roots are deliberate persistent state used to test root items, received UUIDs, cleaner behavior, and metadata references. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs, user namespace support. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 300 | Create subvolume './subvol' | Create subvolume 'subvol/subsubvol' | drwxr-xr-x fsgqa fsgqa ./ | drwxr-xr-x fsgqa fsgqa ./subvol | -rw-r--r-- fsgqa fsgqa ./subvol/1 | -rw-r--r-- fsgqa fsgqa ./subvol/2 | -rw-r--r-- fsgqa fsgqa ./subvol/3 | ... (17 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
