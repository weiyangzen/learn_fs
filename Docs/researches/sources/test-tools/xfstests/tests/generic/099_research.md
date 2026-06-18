# sources/test-tools/xfstests/tests/generic/099

## Purpose

-> 3 extra ACEs: MASK, GROUP, USER -> the GROUP compares with egid of process _and_ the supplementary groups (as found in /etc/group) The test is registered with `_begin_fstest acl auto quick perms` and falls into the ACL/permission, xattr, permission area.

## Important APIs, Types, and Functions

This is an xfstests bash test, so its public interface is the executable script named `099` plus the `_begin_fstest` metadata consumed by the xfstests runner. It imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr` and gates execution with `_require_test`, `_require_runas`, `_require_acls`. Local helpers are none declared. The script uses harness variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`, `$XFS_IO_PROG`, and feature-specific helper programs from the common libraries.

## Control Flow

The script follows the standard xfstests shape: source `common/preamble`, declare metadata, import helper libraries, reject unsupported environments with `_require_*` checks, prepare either `$TEST_DIR` or a freshly made scratch filesystem, run focused filesystem operations, and report success through the final status/exit path. Key operational lines are:

- Line 72: `chmod u=rwx file1`
- Line 73: `chmod g=rw- file1`
- Line 74: `chmod o=r-- file1`
- Line 75: `chown $acl1:$acl2 file1`
- Line 92: `chmod u+w file1`
- Line 263: `chown -R 12345:54321 root`

Validation is performed by deterministic command output, helper comparisons, remount/crash simulation, or silence from the harness. Notable validation lines are:

- Line 81: `chacl -l file1 | _acl_filter_id`
- Line 140: `chacl u::---,g::---,o::---,u:$acl2:r-x file1 2>&1 | _acl_filter_id`
- Line 153: `chacl u::---,g::---,o::---,g:$acl2:r-x file1 2>&1 | _acl_filter_id`
- Line 217: `chacl -l acldir | _acl_filter_id`
- Line 222: `chacl -l file2 | _acl_filter_id`
- Line 229: `chacl -l file3 | _acl_filter_id`

## State and Persistence Behavior

The test state lives in files and directories under `$TEST_DIR` or `$SCRATCH_MNT`, temporary files under `$tmp.*`, and, where applicable, scratch-device metadata. Cleanup state is handled through `_cleanup()`, `rm -f $tmp.*`. Persistence is intentionally exercised through operations such as sync, fsync, unmount/remount, `_scratch_cycle_mount`, `_test_cycle_mount`, or dm-flakey replay when those commands appear. The script does not persist configuration outside the mounted test filesystem except for normal xfstests result logs.

## Dependencies and Integration Points

Integration is with the xfstests runner, `common/preamble`, imported common libraries, the scratch/test mount configuration, and external utilities requested by the `_require_*` gates. Command dependencies visible in the file include xfs_io/fio/fsx/aio/fsstress/ACL/xattr/reflink/dedupe/LVM/scsi-debug helpers when they are referenced by the listed operations. The expected-output file for this numbered test and `$seqres.full` are the main reporting surfaces for the harness.

## Risks and Edge Cases

The expected output is sensitive to namespace support, user/group setup, mount options, and filtered id/name rendering. Because this is a generic test, a skipped `_require_*` check usually means the environment lacks the feature under test rather than that the filesystem passed.

## Test Signals

A good run produces the scripted filtered output, no unexpected stderr, no unfiltered dmesg failures, and the final status path `status=0; exit`. Regression signals include changed md5/cmp/stat/getfattr output, failed `_verify_reflink` or `_compare_range`, missed ENOSPC/failure reporting, stale metadata after remount or crash replay, and unexpected notrun results from changed helper capability detection.
