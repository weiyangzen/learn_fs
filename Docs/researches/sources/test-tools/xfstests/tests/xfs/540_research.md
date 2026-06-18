<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/540 -->
# sources/test-tools/xfstests/tests/xfs/540

## Purpose

Functional test for xfsprogs commit: 5f062427 ("xfs_repair: validate alignment of inherited rt extent hints") This xfs_repair patch detects directories that are configured to propagate their realtime and extent size hints to newly created realtime files when the hint size isn't aligned to the size of a realtime extent. Since this is a test of userspace tool functionality, we don't need kernel support, which in turn means that we omit _require_realtime.  Note that XFS allows users to configure realtime extent size geometry and set RTINHERIT flags even if the filesystem itself does not have a realtime volume attached. This file is a targeted corruption regression. It creates a scratch filesystem, mutates a precise XFS metadata field or structure, and then relies on mount, scrub, repair, or verifier behavior to prove the bug stays fixed.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto repair fuzzers` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `rootino`, `rtextsz_blks`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_scratch_non_zoned`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs_xfs -r extsize=7b | _filter_mkfs > $seqres.full 2>$tmp.mkfs`, `_scratch_mount >> $seqres.full 2>&1`, `_scratch_unmount`, `_scratch_xfs_set_metadata_field core.extsize $((rtextsz_blks + 1)) "inode $rootino" >> $seqres.full`, `_scratch_xfs_set_metadata_field core.rtinherit 1 "inode $rootino" >> $seqres.full`, `_scratch_xfs_set_metadata_field core.extszinherit 1 "inode $rootino" >> $seqres.full`, `_scratch_xfs_db -x -c "inode $rootino" -c 'print' >> $seqres.full`, `_scratch_xfs_repair -n >> $seqres.full 2>&1 && \`; plus 1 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db metadata reads/writes, common/fuzzy helpers, scratch mount cycles, and xfstests filters that normalize expected diagnostics. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is tight coupling to on-disk format details; feature gates, block-size calculations, and expected verifier messages must track XFS format changes. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 540`; `Format and mount`; `Misconfigure the root directory`; `Detect misconfigured directory`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/540 -->
