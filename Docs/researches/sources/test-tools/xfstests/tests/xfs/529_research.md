<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/529 -->
# sources/test-tools/xfstests/tests/xfs/529

## Purpose

Verify that XFS does not cause inode fork's extent count to overflow when adding a single extent while there's no possibility of splitting an existing mapping. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota prealloc` and imports common modules: `preamble`, `filter`, `quota`, `inject`, `populate`. Local helper functions: none Key environment variables or shell state names include `bsize`, `fillerdir`, `nextents`, `nr_blks`, `nr_free_blks`, `nr_quotas`, `nr_quotas_per_block`, `selector`, `testfile`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_quota`, `_require_xfs_debug`, `_require_test_program "punch-alternating"`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_error_injection "reduce_max_iextents"`, `_require_xfs_io_error_injection "bmap_alloc_minlen_extent"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full`, `_scratch_mount -o uquota >> $seqres.full`, `_xfs_force_bdev data $SCRATCH_MNT`, `_scratch_inject_error reduce_max_iextents 1`, `$XFS_IO_PROG -f -s -c "pwrite $((i * bsize)) $bsize" $testfile \`, `nextents=$(_xfs_get_fsxattr nextents $testfile)`, `_scratch_inject_error reduce_max_iextents 0`, `$XFS_IO_PROG -f -c "falloc $((i * bsize)) $bsize" $testfile \`; plus 6 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 529`; `Format and mount fs`; `* Delalloc to written extent conversion`; `Inject reduce_max_iextents error tag`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/529 -->
