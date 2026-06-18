# sources/test-tools/xfstests/tests/btrfs/131

## Purpose

`sources/test-tools/xfstests/tests/btrfs/131` is btrfs fstests case `131`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Test free space tree mount options, 3 options involved: - No space cache - Old (deprecated) v1 space cache - New (default) v2 space cache Future proof against btrfs-progs making space_cache=v2 filesystems by default. Mount options might interfere. When the free space tree is not enabled: -o space_cache=v1: keep using the old free space cache -o space_cache=v2: enable the free space tree

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick` declares tags `auto quick`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_command inspect-internal dump-super`, `_require_btrfs_fs_feature free_space_tree`, `_require_btrfs_v1_cache`; local shell helpers: `mkfs_v1()`, `mkfs_v2()`, `check_fst_compat()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command inspect-internal dump-super`; `_require_btrfs_fs_feature free_space_tree`; `_require_btrfs_v1_cache`; `_scratch_mkfs >/dev/null 2>&1`; `_scratch_mount -o clear_cache,space_cache=v1`; `_scratch_mount -o space_cache=v2`; `_scratch_mount -o space_cache=v1`; `_scratch_mount -o clear_cache,space_cache=v2`; `_try_scratch_mount -o nospace_cache >/dev/null 2>&1 || echo "mount failed"`; `_try_scratch_mount -o space_cache=v1 >/dev/null 2>&1 || echo "mount failed"`; `_scratch_mount`; `_scratch_mount -o clear_cache`; `_scratch_mount -o clear_cache,nospace_cache`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
