<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/496 -->
# sources/test-tools/xfstests/tests/xfs/496

## Purpose

Populate a XFS filesystem and fuzz every single-leafn-format dir block field. Use xfs_repair to fix the corruption. This file is one of the single-leafn directory block fuzzing variants. The three variants share the same target object and differ by whether corruption is repaired offline, repaired online, or left unrepaired for verifier coverage.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest dangerous_fuzzers repair fuzzers_repair` and imports common modules: `preamble`, `filter`, `populate`, `fuzzy`. Local helper functions: none Key environment variables or shell state names include `blk_sz`, `inum`, `leaf_offset`.

Requirements and feature gates: `_require_scratch_xfs_fuzz_fields`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_populate_cached nofill > $seqres.full 2>&1`, `_scratch_mount`, `_scratch_unmount`, `_scratch_xfs_fuzz_metadata '' 'offline' "inode ${inum}" "dblock ${leaf_offset}" >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is the populated `S_IFDIR.FMT_LEAFN` directory, calculated directory leaf block offset, and common/fuzzy repair-mode selection. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is false coverage if the populated image no longer creates a single-leafn directory at the expected offset, or if online repair support is not actually present when the tag implies it. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 496`; `Format and populate`; `Find single-leafn-format dir block`; `Fuzz single-leafn-format dir block`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/496 -->
