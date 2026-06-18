<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/597 -->
# sources/test-tools/xfstests/tests/xfs/597

## Purpose

Make sure that the kernel and userspace agree on which byte sequences are ASCII uppercase letters, and how to convert them. This file targets ASCII case-insensitive directory semantics. It builds leaf-format directories or attributes with names that stress kernel/userspace case folding and obfuscation behavior.

## Important APIs, Types, and Functions

This is a Bash xfstests case, so its API surface is the xfstests shell harness rather than exported library types. It starts with `_begin_fstest auto ci dir` and imports common modules: `preamble`, `filter`. Local helper functions: none Key environment variables or shell state names include `dblksz`, `dirsz`, `i`, `name`, `nr_dirents`.

Requirements and feature gates: `_require_scratch`, `_require_xfs_mkfs_ciname`, `_require_xfs_ciname`. Recorded fix annotations: `_fixed_by_kernel_commit a9248538facc xfs: stabilize the dirent name transformation function used for ascii-ci dir hash computation`, `_fixed_by_kernel_commit 9dceccc5822f xfs: use the directory name hash function for dir scrubbing`.

## Control Flow

The script follows the normal xfstests lifecycle: source `common/preamble`, declare tags, import helper modules, enforce prerequisites, build a scratch or test scenario, run XFS/xfsprogs operations, filter diagnostics, and exit with `status=0` on success. Important command signals in this file are: `_scratch_mkfs -n version=ci > $seqres.full`, `_scratch_mount`, `dblksz=$(_xfs_get_dir_blocksize "$SCRATCH_MNT")`.

For this specific test, the scenario is driven by the header purpose and the command sequence above. Scratch filesystems are formatted or populated, mounted and unmounted as needed, and the test oracle is either command success, normalized diagnostic output, a remount/repair check, a quota/accounting comparison, or a silent no-crash/no-livelock completion.

## State and Persistence Behavior

Persistent state is confined to the scratch filesystem, optional test-directory artifacts under `$TEST_DIR`, temporary files under `$tmp.*`, and the xfstests result streams `$seqres` and `$seqres.full`. The script can alter on-disk XFS metadata through xfs_db helpers, mount options, quota state, realtime allocation policy, error-injection sysfs/debug knobs, or generated dump/metadump images depending on the scenario. Cleanup hooks remove temporary files, reset debug knobs, unmount scratch devices, or stop stress-scrub helpers when the test defines them.

## Dependencies and Integration Points

The integration surface is mkfs `-n version=ci`, XFS case-insensitive name helpers, directory block sizing, metadump or repair verification, and locale-sensitive byte generation. The source integrates with xfstests golden-output comparison through the matching `.out` file when present, common filter functions for nondeterministic values, and xfsprogs/kernel feature probes that turn unsupported environments into `_notrun` instead of failure.

## Risks and Edge Cases

The risk is locale and name-transformation drift; the script requires `LANG=C` where byte generation must not become UTF-8 text processing. Additional edge cases include stale mounts after injected corruption, kernel debug builds changing verifier behavior, xfsprogs output drift, nondefault block sizes or allocation group geometry, and cleanup paths that must reset any background process or sysfs knob before the next test runs.

## Test Signals

The primary pass signal is that the script reaches `status=0` without unexpected stdout/stderr beyond normalized expected output. Failures usually appear as `_require_*` skips, command nonzero exits, `_check_scratch_fs` or repair findings, unexpected dmesg after `_check_dmesg`, quota/du mismatches, diff output between generated reports, or missing expected health/scrub diagnostics. Expected-output sidecar starts with: `QA output created by 597`; `ln: failed to create hard link 'SCRATCH_MNT/lol/'$'\340': File exists`; `ln: failed to create hard link 'SCRATCH_MNT/lol/'$'\341': File exists`; `ln: failed to create hard link 'SCRATCH_MNT/lol/'$'\342': File exists`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/597 -->
