<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/527 -->
# sources/test-tools/xfstests/tests/xfs/527

## Purpose

Regression test for incorrect validation of ondisk dquot type flags when we're switching between group and project quotas while mounting a V4 filesystem.  This test doesn't actually force the creation of a V4 fs because even V5 filesystems ought to be able to switch between the two without triggering corruption errors. The appropriate XFS patch is: xfs: fix incorrect root dquot corruption error when switching group/project quota types unreliable_in_parallel: dmesg check can pick up corruptions from other tests. Need to filter corruption reports by short scratch dev name. This file exercises quota accounting or quota scrub behavior on XFS. It combines scratch quota mount options with block usage, reflink, CoW, or stress operations and compares kernel accounting to user-visible reports.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick quota unreliable_in_parallel` and imports common modules: `preamble`, `quota`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_xfs_debug`, `_require_quota`, `_require_scratch`, `_require_check_dmesg`, `_require_prjquota $SCRATCH_DEV`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full`, `$here/src/feature -G $SCRATCH_DEV || echo "group quota didn't mount?"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/quota, xfs_quota reports, repquota-compatible VFS quota checks, scratch remounts, and any reflink or fsstress helpers used to generate accounting pressure. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is delayed accounting and preallocation state; tests often sync, remount, or force quotacheck so speculative CoW reservations do not look like real regressions. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 527`; `Format filesystem`; `Mount with project quota`; `Mount with group quota`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/527 -->
