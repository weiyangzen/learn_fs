<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/507 -->
# sources/test-tools/xfstests/tests/xfs/507

## Purpose

Regression test for kernel commit: 394aafdc15da ("xfs: widen inode delalloc block counter to 64-bits") Try to overflow i_delayed_blks by setting the largest cowextsize hint possible, creating a sparse file with a single byte every cowextsize bytes, reflinking it, and retouching every written byte to see if we can create enough speculative COW reservations to overflow i_delayed_blks. This is a focused xfstests shell regression. It encodes an XFS behavior, userspace-tool contract, or maintenance check as a scratch/test filesystem scenario.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto clone` and imports common modules: `preamble`, `reflink`, `filter`. Local helper functions: `_cleanup`, `count_file_fork_blocks`, `count_fork_blocks`. Key environment variables or shell state names include `LARGE_SCRATCH_DEV`, `MAXEXTLEN`, `allocated_fsblocks`, `allocated_stat_blocks`, `attrblocks`, `blks_needed`, `blksz`, `cowblocks`, `cowextsize_bytes`, `curr_cowextsize_str`; plus 6 more.

Requirements and feature gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_loop`, `_require_xfs_debug	# needed for xfs_bmap -c`, `_require_congruent_file_oplen $SCRATCH_MNT $((MAXEXTLEN * fs_blksz))`, `_require_fs_space $SCRATCH_MNT 1234567`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `$XFS_IO_PROG -f -c "truncate $loop_file_sz" $loop_file`, `curr_cowextsize_str="$($XFS_IO_PROG -c 'cowextsize' "$huge_file")"`, `$XFS_IO_PROG -c "pwrite $off 1" "$huge_file" > /dev/null`, `$XFS_IO_PROG -c "bmap $args -l -p -v" "$huge_file" > $tmp.extents`, `LARGE_SCRATCH_DEV=yes _check_xfs_filesystem $loop_dev none none`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the xfstests common harness, scratch filesystem lifecycle helpers, xfsprogs commands, and golden-output filtering through `seqres.full` and `.out` files. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is environment sensitivity: missing xfsprogs features, kernel feature flags, scratch geometry, runtime load, or non-normalized diagnostics can produce false failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 507`; `Format and mount`; `Create crazy huge file`; `Reflink crazy huge file`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/507 -->
