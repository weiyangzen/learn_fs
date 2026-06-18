<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/541 -->
# sources/test-tools/xfstests/tests/xfs/541

## Purpose

Regression test for kernel commits: 83193e5ebb01 ("xfs: correct the narrative around misaligned rtinherit/extszinherit dirs") 5aa5b278237f ("xfs: don't expose misaligned extszinherit hints to userspace") 0e2af9296f4f ("xfs: improve FSGROWFSRT precondition checking") 0925fecc5574 ("xfs: fix an integer overflow error in xfs_growfs_rt") b102a46ce16f ("xfs: detect misaligned rtinherit directory extent size hints") Test for xfs_growfs to make sure that we can add a realtime device and set its extent size hint at the same time. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick realtime growfs` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `SCRATCH_RTDEV`, `XFS_MAX_RTEXTSIZE`, `after_extszhint`, `after_rtextsz_blocks`, `file_extszhint`, `grow_extszhint`, `new_extszhint`, `new_rtextsz`, `new_rtextsz_blocks`, `res`; plus 1 more.

Requirements and feature gates: `_require_realtime`, `_require_scratch`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `SCRATCH_RTDEV="" _scratch_mkfs | _filter_mkfs 2> $tmp.mkfs >> $seqres.full`, `_try_scratch_mount || _notrun "Can't mount file system"`, `if [ $new_rtextsz -gt $XFS_MAX_RTEXTSIZE ]; then`, `$XFS_IO_PROG -c 'chattr +t' -c "extsize $new_extszhint" $SCRATCH_MNT`, `after_extszhint=$($XFS_IO_PROG -c 'stat' $SCRATCH_MNT | \`, `echo $XFS_GROWFS_PROG -e $new_rtextsz_blocks -r $SCRATCH_MNT >> $seqres.full`, `$XFS_GROWFS_PROG -e $new_rtextsz_blocks -r $SCRATCH_MNT >> $seqres.full 2> $tmp.growfs`, `grow_extszhint=$($XFS_IO_PROG -c 'stat' $SCRATCH_MNT | \`; plus 5 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 541`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/541 -->
