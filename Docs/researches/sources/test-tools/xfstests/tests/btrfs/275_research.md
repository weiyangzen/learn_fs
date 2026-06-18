# sources/test-tools/xfstests/tests/btrfs/275

## Purpose
Test that no xattr can be changed once btrfs property is set to RO. Create a test file. Attempt to change values of RO (property) filesystem. Check the values of RO (property) filesystem are not changed. Attempt to remove xattr from RO (property) filesystem. Check if xattr still exist. Change filesystem property RO to false Change the xattrs after RO is false. Get the changed values. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick attr`. Requirement and capability gates: line 17: `_require_attrs`; line 18: `_require_btrfs_command "property"`; line 19: `_require_scratch`. Local helper surface: `set_xattr()` (line 26), `get_xattr()` (line 34), `del_xattr()` (line 41). Important command/API calls include line 15: `_fixed_by_kernel_commit b51111271b03 "btrfs: check if root is readonly while setting security xattr"`; line 17: `_require_attrs`; line 18: `_require_btrfs_command "property"`; line 19: `_require_scratch`; line 21: `_scratch_mkfs >> $seqres.full 2>&1`; line 22: `_scratch_mount`; line 29: `$SETFATTR_PROG -n "user.one" -v $value $FILENAME 2>&1 | _filter_scratch`; line 30: `$SETFATTR_PROG -n "security.one" -v $value $FILENAME 2>&1 | _filter_scratch`; line 31: `$SETFATTR_PROG -n "trusted.one" -v $value $FILENAME 2>&1 | _filter_scratch`; line 36: `_getfattr --absolute-names -n "user.one" $FILENAME 2>&1 | _filter_scratch`; line 37: `_getfattr --absolute-names -n "security.one" $FILENAME 2>&1 | _filter_scratch`; line 38: `_getfattr --absolute-names -n "trusted.one" $FILENAME 2>&1 | _filter_scratch`; line 43: `$SETFATTR_PROG -x "user.one" $FILENAME 2>&1 | _filter_scratch`; line 44: `$SETFATTR_PROG -x "security.one" $FILENAME 2>&1 | _filter_scratch`. It documents fixed kernel commit context at line 15: `_fixed_by_kernel_commit b51111271b03 \`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick attr`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 275 | ro=true | setfattr: SCRATCH_MNT/foo: Read-only file system | setfattr: SCRATCH_MNT/foo: Read-only file system | setfattr: SCRATCH_MNT/foo: Read-only file system | # file: SCRATCH_MNT/foo | user.one="1" |  | ... (39 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
