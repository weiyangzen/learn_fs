<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/568 -->
# sources/test-tools/xfstests/tests/xfs/568

## Purpose

Tests `xfsrestore -x` which handles an wrong inode in a dump, with the multi-level dumps where we hit an issue during development. This procedure is cribbed from: xfs/065: Testing incremental dumps and cumulative restores with different operations for each level This file exercises xfsdump/xfsrestore multi-level restore behavior with the `-x` option for dumps containing a wrong or fake inode. It derives from older dump/restore tests but narrows the scenario to a restore regression.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto dump` and imports common modules: `preamble`, `filter`, `dump`, `quota`. Local helper functions: `_cleanup`, `_list_dir`. Key environment variables or shell state names include `LC_COLLATE`, `__dir`, `dumpfile`, `fake_inum`, `i`, `inums`, `num_dumps`, `opt`, `root_inum`.

Requirements and feature gates: `_require_xfs_io_command "falloc"`, `_require_scratch`, `_require_xfsrestore_xflag`. Recorded fix annotations: `_fixed_by_git_commit xfsdump XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `find $__dir -exec $here/src/lstat64 -t {} \; |\`, `"XXXXXXXXXXXX xfsrestore: fix rootdir due to xfsdump bulkstat misuse"`, `_scratch_mkfs_xfs >> $seqres.full`, `_scratch_mount`, `$here/src/feature -U $SCRATCH_DEV && \`, `$here/src/feature -G $SCRATCH_DEV && \`, `$here/src/feature -P $SCRATCH_DEV && \`, `_scratch_unmount`; plus 2 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfsdump/xfsrestore, hardlink and incremental dump state, scratch population, and deterministic directory listing filters used to compare restored trees. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is output instability from inode numbers, directory sizes, quota state, and dump timestamps; the script filters variable fields and disables quotas where needed. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 568`; `Do the incremental dumps`; `Listing of what files we have at level 0:`; `dumpdir/addeddir1 XXX drwxr-xr-x 0,0`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/568 -->
