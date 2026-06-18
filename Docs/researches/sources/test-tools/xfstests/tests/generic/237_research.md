# sources/test-tools/xfstests/tests/generic/237

## Purpose

Check user B can setfacl a file which belongs to user A See also http://marc.info/?l=linux-btrfs&m=127434445620298&w=2 only Linux supports fallocate get dir. It is registered with `_begin_fstest auto quick acl perms` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `237` plus `_begin_fstest auto quick acl perms`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`. Capability gates: `_require_test`, `_require_runas`, `_require_acls`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 46: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 41 `echo "Expect to FAIL"`, line 44 `echo "Test over."`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 21: `rm -f $tmp.*`
- Line 22: `[ -n "$TEST_DIR" ] && rm -rf $TEST_DIR/$seq.dir1`
- Line 26: `_require_test`
- Line 34: `rm -rf $seq.dir1`
- Line 35: `mkdir $seq.dir1`
- Line 38: `touch file1`
- Line 39: `chown $acl1:$acl1 file1`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `acl`, `perms`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/attr`, and uses capability gates such as `_require_test`, `_require_runas`, `_require_acls`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
