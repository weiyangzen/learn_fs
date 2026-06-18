# sources/test-tools/xfstests/tests/btrfs/264

## Purpose
Compression and nodatacow are mutually exclusive. Besides ioctl, there is another way to setting compression via xattrs, and shouldn't produce invalid combinations. To prevent mix any compression-related options with nodatacow, FS_NOCOMP_FL is also rejected by ioctl as well as FS_COMPR_FL on nodatacow files. To align with it, no and none are also unacceptable in this test. The regression is fixed by a patch with the following subject: btrfs: do not allow compression on nodatacow files FS_NOCOMP_FL bit isn't recognized by chattr/lsattr before e2fsprogs 1.46.2. In this subset it primarily covers Btrfs filesystem behavior through xfstests shell orchestration.

## Important APIs, Types, and Functions
The fstest declaration is `auto quick compress attr`. Requirement and capability gates: line 24: `_require_scratch`; line 25: `_require_attrs`; line 26: `_require_chattr C`. Local helper surface: no custom shell functions beyond the linear test body. Important command/API calls include line 24: `_require_scratch`; line 25: `_require_attrs`; line 26: `_require_chattr C`; line 28: `_scratch_mkfs >>$seqres.full 2>&1`; line 29: `_scratch_mount`; line 34: `$SETFATTR_PROG -n "btrfs.compression" -v "$2" "$1" |& _filter_scratch`; line 40: `check_compression() # $1: filename`; line 45: `echo "$1: Compression is set" | _filter_scratch`; line 47: `echo "$1: Compression is not set" | _filter_scratch`; line 55: `touch "$test_file"`; line 59: `check_compression "$test_file"`.

## Control Flow
The control flow follows the xfstests pattern: source the common preamble, declare `_begin_fstest auto quick compress attr`, install cleanup if needed, enforce requirements, then formats scratch storage, mounts the test filesystem, runs btrfs check or xfstests scratch checks. The script then performs its focused state transition and relies on explicit command failures, `_fail`, filtered stdout, content comparisons, filesystem checks, or expected output matching to detect regressions. Cleanup hooks remove temporary send streams, loop devices, scratch pool devices, or `$tmp.*` artifacts when the test defines them.

## State and Persistence Behavior
The script owns scratch filesystem state and normally reformats, mounts, unmounts, or checks it through xfstests helpers. Sync, remount, unmount, receive, or device-scan boundaries are used to separate in-memory success from on-disk or kernel-global persistence.

## Dependencies and Integration Points
This file integrates with xfstests `common/preamble`, Btrfs common helpers, scratch-device lifecycle helpers, output filters, and the Btrfs kernel interfaces reached through standard xfstests common helpers and btrfs-progs. It also depends on the adjacent expected-output file for stable golden-output comparison: `QA output created by 264 | SCRATCH_MNT/foo: Compression is set | SCRATCH_MNT/foo: Compression is not set | SCRATCH_MNT/foo: Compression is set | SCRATCH_MNT/foo: Compression is not set | SCRATCH_MNT/foo: Compression is set | setfattr: SCRATCH_MNT/bar: Invalid argument | setfattr: SCRATCH_MNT/bar: Invalid argument | ... (11 expected-output lines total)`.

## Risks and Edge Cases
the main risk is silent metadata or persistence regression that only appears after remount, receive, check, or explicit content comparison. Test reliability can also depend on mkfs defaults, sector size, nodesize, mount options, compression settings, discard support, device size, and whether helper commands support the specific subcommands used by the script.

## Test Signals
Primary pass signals are successful command completion, no unexpected stderr after filtering, expected `.out` text, clean `btrfs check` or `_check_scratch_fs` results when present, and matching file digests/fssum/byte dumps after replay or remount. Any mismatch in expected output, missing qgroup/device/snapshot state, uncorrected corruption, unexpected swapon success/failure, or receive/check failure indicates a regression for this source.
