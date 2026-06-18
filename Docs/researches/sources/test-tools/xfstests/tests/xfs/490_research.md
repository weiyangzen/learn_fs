<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/490 -->
# sources/test-tools/xfstests/tests/xfs/490

## Purpose

Test a corruption when the directory structure and the inobt thinks the inode is free, but the inode on disk thinks it is still in use. This case test same bug (upstream linux commit ee457001ed6c) as xfs/132, but through different code path. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick` and imports common modules: `preamble`, `filter`. Local helper functions: `filter_dmesg`. Key environment variables or shell state names include `agcount`, `agi`, `blksz`, `fmask`, `freecount`, `inum`.

Requirements and feature gates: `_require_scratch_nocheck`, `_require_xfs_mkfs_finobt`, `_require_xfs_nocrc`, `_require_no_xfs_debug`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `local warn1="Internal error xfs_trans_cancel.*fs/xfs/xfs_trans\.c.*"`, `sed -e "s#$warn1#Intentional error in xfs_trans_cancel#"`, `_scratch_mkfs_xfs -m crc=0,finobt=0 | _filter_mkfs 2>$tmp.mkfs >> $seqres.full`, `blksz=$(_scratch_xfs_get_sb_field blocksize)`, `agcount=$(_scratch_xfs_get_sb_field agcount)`, `_scratch_mount $mount_opt`, `$XFS_IO_PROG -fc "pwrite 0 $blksz" -c fsync $SCRATCH_MNT/dir/testfile >> $seqres.full`, `_scratch_unmount`; plus 6 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 490`; `SCRATCH_MNT/dir/newfile: Structure needs cleaning`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/490 -->
