<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/488 -->
# sources/test-tools/xfstests/tests/xfs/488

## Purpose

Populate a XFS filesystem and fuzz every group dquot field. Do not fix the filesystem, to test metadata verifiers. This file belongs to the XFS metadata fuzzing block. It uses populated scratch filesystems and common/fuzzy helpers to mutate a specific on-disk structure, then deliberately exercises verifier behavior with the repair mode encoded in its tags and `_scratch_xfs_fuzz_metadata` arguments.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers fuzzers_norepair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`, `quota`. Local helper functions: none Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`, `_require_quota`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `$here/src/feature -G $SCRATCH_DEV || _notrun "group quota disabled"`, `_scratch_unmount`, `_scratch_xfs_set_quota_fuzz_ids`, `_scratch_xfs_fuzz_metadata '' 'none' "dquot -g $id" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The important integration surface is xfs_db-driven metadata addressing, cached population images, mount or scrub/repair validation, and the xfstests dangerous_fuzzers gating that keeps destructive corruption tests out of ordinary quick runs. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The main risk is that target metadata layout assumptions can drift as XFS formats evolve; skips and feature requirements must remain accurate so the test corrupts the intended structure instead of producing unrelated mount, xfs_db, or repair failures. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 488`; `Format and populate`; `Fuzz group 0 dquot`; `Done fuzzing dquot`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/488 -->
