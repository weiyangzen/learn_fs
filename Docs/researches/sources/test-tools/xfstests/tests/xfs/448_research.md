<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/448 -->
# sources/test-tools/xfstests/tests/xfs/448

## Purpose

Regression test for commit: 46c59736d809 ("xfs: harden directory integrity checks some more") If a malicious XFS contains a block+ format directory wherein the directory inode's core.mode is corrupted, and there are subdirectories of the corrupted directory, an attempt to traverse up the directory tree by running xfs_scrub will crash the kernel in __xfs_dir3_data_check. This file is a targeted corruption regression. It creates a scratch filesystem, mutates a precise XFS metadata field or structure, and then relies on mount, scrub, repair, or verifier behavior to prove the bug stays fixed.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto quick fuzzers` and imports common modules: `preamble`, `filter`, `populate`. Local helper functions: none Key environment variables or shell state names include `dino`, `getmode`, `setmode`, `subdgen`, `subdino`.

Requirements and feature gates: `_require_scratch_nocheck`, `_require_xfs_io_command "scrub"`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs | _filter_mkfs > $seqres.full 2> $tmp.mkfs`, `_scratch_mount`, `_scratch_unmount`, `subdgen=$(_scratch_xfs_get_metadata_field "core.gen" "inode $subdino")`, `_scratch_xfs_set_metadata_field "core.mode" "$setmode" "inode $dino" >> $seqres.full`, `getmode=$(_scratch_xfs_get_metadata_field "core.mode" "inode $dino")`, `$XFS_IO_PROG -x -c "scrub parent $subdino $subdgen" ${SCRATCH_MNT} >> $seqres.full`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_db metadata reads/writes, common/fuzzy helpers, scratch mount cycles, and xfstests filters that normalize expected diagnostics. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is tight coupling to on-disk format details; feature gates, block-size calculations, and expected verifier messages must track XFS format changes. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 448`; `Silence is golden`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/448 -->
