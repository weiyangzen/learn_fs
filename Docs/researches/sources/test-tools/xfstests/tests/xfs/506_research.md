<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/506 -->
# sources/test-tools/xfstests/tests/xfs/506

## Purpose

Basic tests of the xfs_spaceman health command. This file exercises XFS online scrub, health reporting, or repair-adjacent behavior. It uses the xfstests scratch device plus xfs_scrub or xfs_spaceman commands to turn metadata health into a test oracle.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick health` and imports common modules: `preamble`, `fuzzy`, `filter`. Local helper functions: `query`, `query_health`, `query_sick`. Key environment variables or shell state names include only standard xfstests variables such as `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres`, and `tmp` are used

Requirements and feature gates: `_require_scratch_nocheck`, `_require_scrub`, `_require_xfs_spaceman_command "health"`, `_require_scratch_xfs_scrub`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_cycle_mount # make sure we haven't run quotacheck on this mount`, `$XFS_SPACEMAN_PROG -c "health" $SCRATCH_MNT`, `_scratch_scrub -n >> $seqres.full`, `$XFS_SPACEMAN_PROG -c "$@" $SCRATCH_MNT | tee -a $seqres.full`, `_scratch_unmount`, `_scratch_xfs_db -x -c 'sb 1' -c 'fuzz -d magicnum random' >> $seqres.full`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is common/fuzzy, xfs_io scrub commands, xfs_spaceman health output, scratch remounts, and feature-specific scrub prerequisites. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that online health state is cached and feature-dependent; the scripts force mount cycles or explicit scrub passes to avoid reading stale state. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 506`; `Health status has not been collected for this filesystem.`; `Please run xfs_scrub(8) to remedy this situation.`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/506 -->
