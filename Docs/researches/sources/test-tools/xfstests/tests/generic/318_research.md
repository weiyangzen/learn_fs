# sources/test-tools/xfstests/tests/generic/318

## Purpose

Check get/set ACLs to/from disk with a user namespace. A new file will be created and ACLs set on it from both inside a userns and from init_user_ns. We check that the ACL is is correct from both inside the userns and also from init_user_ns. We will then unmount and remount the file system and check the ACL from both inside the userns and from init_user_ns to show that the correct uid/gid in the ACL was flushed and brought back from disk only Linux supports user namespace. It is registered with `_begin_fstest acl attr auto quick perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `318` plus `_begin_fstest acl attr auto quick perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_scratch`, `_require_acls`, `_require_ugid_map`, `_require_userns`. Local functions: `_cleanup`, `_getfacl_filter_nsid`, `_print_getfacls`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 29: `nsexec=$here/src/nsexec`
- Line 30: `file=$SCRATCH_MNT/file1`
- Line 39: `ns_acl1=0`
- Line 40: `ns_acl2=`expr $acl2 - $acl1``
- Line 41: `ns_acl3=`expr $acl3 - $acl1``
- Line 90: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 59 `echo "From init_user_ns"`, line 62 `echo "From user_ns"`, line 67 `echo "*** MKFS ***" >>$seqres.full`, line 68 `echo "" >>$seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `_scratch_unmount >/dev/null 2>&1`
- Line 34: `_require_scratch`
- Line 43: `_getfacl_filter_nsid()`
- Line 60: `getfacl --absolute-names -n $file 2>/dev/null | _filter_scratch | _getfacl_filter_id`
- Line 63: `$nsexec -U -M "0 $acl1 1000" -G "0 $acl1 1000" getfacl --absolute-names -n $file 2>/dev/null | _filter_scratch | _getfacl_filter_nsid`
- Line 66: `_scratch_unmount >/dev/null 2>&1`
- Line 69: `_scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"`
- Line 70: `_scratch_mount`
- Line 72: `touch $file`
- Line 73: `chown $acl1:$acl1 $file`
- Line 82: `echo "*** Remounting ***"`
- Line 84: `_scratch_sync`
- Line 85: `_scratch_cycle_mount >>$seqres.full 2>&1 || _fail "remount failed"`
- Line 89: `_scratch_unmount >/dev/null 2>&1`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Cycle-mount calls force metadata and extent state through unmount/remount persistence before validation. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `acl`, `attr`, `auto`, `quick`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_scratch`, `_require_acls`, `_require_ugid_map`, `_require_userns`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
