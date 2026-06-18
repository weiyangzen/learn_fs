<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/576 -->
# sources/test-tools/xfstests/tests/xfs/576

## Purpose

Race fsstress and inode btree scrub for a while to see if we crash or livelock. This file belongs to the scrub stress race suite. It formats and mounts scratch XFS, starts common/xfs stress-scrub orchestration, and races fsstress or fsx style mutation against one scrub or online-repair target.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest scrub fsstress_scrub` and imports common modules: `preamble`, `filter`, `fuzzy`, `inject`, `xfs`. Local helper functions: `_cleanup`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch`, `_require_xfs_stress_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_begin_fstest scrub fsstress_scrub`, `_scratch_xfs_stress_scrub_cleanup &> /dev/null`, `_scratch_mkfs > "$seqres.full" 2>&1`, `_scratch_mount`, `_scratch_xfs_stress_scrub -x 'dir' -s "scrub inobt %agno%"`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is `_scratch_xfs_stress_scrub`, its cleanup hook, selected scrub command strings, fsstress operation exclusion flags, and feature gates for realtime, quota, reflink, attributes, rmapbt, or finobt when required. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is nondeterminism: the expected signal is absence of crashes, livelocks, and scrub infrastructure failures, so runtime, load factor, feature availability, and cleanup correctness matter more than fixed stdout. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 576`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/576 -->
