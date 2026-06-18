<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/599 -->
# sources/test-tools/xfstests/tests/xfs/599

## Purpose

Make sure that the kernel and utilities can handle large numbers of dirhash collisions in both the directory and extended attribute structures. This started as a regression test for the new 'hashcoll' function in xfs_db, but became a regression test for an xfs_repair bug affecting hashval checks applied to the second and higher node levels of a dabtree. This file creates extreme directory and xattr hash-collision trees to validate kernel and xfsprogs handling of deep dabtrees with repeated hash values.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto dir` and imports common modules: `preamble`. Local helper functions: `filter_hashvals`. Key environment variables or shell state names include `attr_count`, `attr_db_args`, `blksz`, `crash_attrs`, `crash_dir`, `da_node_block_offset`, `da_records_per_block`, `dblksz`, `dir_count`, `dir_db_args`; plus 3 more.

Requirements and feature gates: `_require_xfs_db_command "hashcoll"`, `_require_xfs_db_command "path"`, `_require_scratch`. Recorded fix annotations: `_fixed_by_git_commit xfsprogs b7b81f336ac xfs_repair: fix incorrect dabtree hashval comparison`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs_repair: fix incorrect dabtree hashval comparison"`, `_scratch_mkfs > $seqres.full`, `_scratch_mount`, `dblksz=$(_xfs_get_dir_blocksize "$SCRATCH_MNT")`, `_scratch_xfs_db -r -c "hashcoll -n $nr_dirents -p $crash_dir $longname"`, `_scratch_xfs_db -r -c "hashcoll -a -n $nr_attrs -p $crash_attrs $longname"`, `_scratch_unmount`, `dir_count="$(_scratch_xfs_db "${dir_db_args[@]}" -c 'print lhdr.count' | awk '{print $3}')"`; plus 3 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db `hashcoll` and `path`, directory/attribute dabtree addressing, hash-value inspection, remount coverage, and later repair checks. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that directory block sizing or name length assumptions may fail to create a two-level dabtree, which would leave the repair hash comparison path untested. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 599`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/599 -->
