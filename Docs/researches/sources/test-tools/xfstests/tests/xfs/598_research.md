<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/598 -->
# sources/test-tools/xfstests/tests/xfs/598

## Purpose

Make sure that metadump obfuscation works for filesystems with ascii-ci enabled. This file validates metadump/mdrestore round trips. It creates a populated or feature-specific filesystem, emits metadumps with option combinations, restores them, and checks the restored scratch filesystem.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto dir ci` and imports common modules: `preamble`. Local helper functions: `_cleanup`. Key environment variables or shell state names include `dblksz`, `dirsz`, `i`, `metadump_file`, `metadump_file_a`, `metadump_file_ao`, `metadump_file_o`, `name`, `nr_dirents`, `testdir`.

Requirements and feature gates: `_require_test`, `_require_scratch`, `_require_xfs_mkfs_ciname`, `_require_xfs_ciname`, `_require_scratch_xfs_mdrestore`. Recorded fix annotations: `_fixed_by_git_commit xfsprogs 10a01bcd xfs_db: fix metadump name obfuscation for ascii-ci filesystems`, `_fixed_by_kernel_commit a9248538facc xfs: stabilize the dirent name transformation function used for ascii-ci dir hash computation`, `_fixed_by_kernel_commit 9dceccc5822f xfs: use the directory name hash function for dir scrubbing`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `"xfs_db: fix metadump name obfuscation for ascii-ci filesystems"`, `_scratch_mkfs -n version=ci > $seqres.full`, `_scratch_mount`, `dblksz=$(_xfs_get_dir_blocksize "$SCRATCH_MNT")`, `_scratch_unmount`, `_scratch_xfs_metadump $metadump_file >> $seqres.full`, `_scratch_xfs_metadump $metadump_file_a -a >> $seqres.full`, `_scratch_xfs_metadump $metadump_file_o -o >> $seqres.full`; plus 6 more.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is xfs_metadump, xfs_mdrestore, loop or scratch restore plumbing, populated test images, and online/offline rebuild skips used to keep verification focused on dump fidelity. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is that obfuscation, feature flags, or restore-device setup can turn a metadata serialization regression into an environment failure; restored filesystems must always be checked after each option variant. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 598`; `metadump`; `metadump a`; `metadump o`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/598 -->
