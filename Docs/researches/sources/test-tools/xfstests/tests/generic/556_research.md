# sources/test-tools/xfstests/tests/generic/556

## Purpose

Test the basic functionality of filesystems with case-insensitive support.

## Important APIs, Types, and Functions

This is a bash xfstests `generic` case registered with `_begin_fstest auto quick casefold`. It imports `./common/preamble`, `./common/filter`, `./common/casefold`, `./common/attr`. Prerequisite and skip gates include `_require_scratch_nocheck`, `_require_scratch_casefold`, `_require_symlinks`, `_require_check_dmesg`, `_require_attrs`. Local helper functions: `filter_touch`, `basic_create_lookup`, `bad_basic_create_lookup`, `test_casefold_lookup`, `test_bad_casefold_lookup`, `do_create_and_remove`, `test_create_and_remove`, `test_casefold_flag_basic`, `test_casefold_flag_removal`, `test_casefold_flag_inheritance`, `test_nesting_sensitive_insensitive_tree_simple`, `test_nesting_sensitive_insensitive_tree_complex`, `test_symlink_with_inexact_name`, `do_test_name_preserve`, `test_name_preserve`, `do_test_dir_name_preserve`, `test_dir_name_preserve`, `test_name_reuse`, `test_create_with_same_name`, `test_file_rename`, `test_toplevel_dir_rename`, `test_casefold_openfd`, `test_casefold_openfd2`, `test_hard_link_lookups`, `test_xattrs_lookups`, `test_lookup_large_directory`, `test_strict_mode_invalid_filename`. External command surfaces and helper binaries visible in the source include `touch`, `mkdir`, `ln`, `mv`, `stat`, `seq`, `mount`. Important harness variables and paths include `SCRATCH_MNT`, `SCRATCH_DEV`, `seqres.full`, `tmp`, `seq`, `FSTYP`, `MOUNT_OPTIONS`.

## Control Flow

The script sources `./common/preamble`, installs any custom cleanup, declares feature requirements, prepares the target filesystem, executes a focused regression sequence, and exits with `status=0` only if all checks pass. Representative source-level operations are: `_require_scratch_nocheck`; `_require_scratch_casefold`; `_require_symlinks`; `_require_check_dmesg`; `_require_attrs`; `sdev="\($(_short_dev ${SCRATCH_DEV})\)"`; `pt_file1=$(echo -e "coração")`; `pt_file2=$(echo -e "corac\xcc\xa7\xc3\xa3o" | tr a-z A-Z)`; `fr_file2=$(echo -e "french_caf\xc3\xa9.txt")`.

## State and Persistence Behavior

The test formats and mounts the scratch filesystem, mutating disposable files under `SCRATCH_MNT`; uses explicit sync/fsync/remount points to force persistence boundaries. Cleanup is handled by the preamble and any local `_cleanup` function, commonly removing `$tmp.*`, unmounting/remounting scratch storage, or undoing activated device-mapper, swap, quota, DAX, encryption, or process state.

## Dependencies and Integration Points

The file integrates with the xfstests harness, the `generic` group dispatcher, filesystem-specific `_require_*` probes, and userspace tools such as xfs_io, fsx, fsstress, fscrypt/keyctl, quota tools, device-mapper helpers, or small compiled programs under `$here/src` when referenced. It is intended to be run by the xfstests runner with configured `TEST_DIR`, `SCRATCH_DEV`, and mount/mkfs options rather than as a standalone shell script.

## Risks and Edge Cases

environmental skips and helper availability can dominate failures, so `_require_*` gates are part of the contract. Because stdout is normalized by filters and detailed logs go to `$seqres.full`, apparent behavior can differ between supported filesystems, missing helper binaries, incompatible block sizes, and kernel versions with or without the referenced regression fixes.

## Test Signals

normalized stdout is compared with `generic/556.out`. Skips from `_require_*` gates are expected on unsupported filesystems or hosts.
