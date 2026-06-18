# sources/test-tools/xfstests/tests/generic/360

## Purpose

Test symlink to very long path, check symlink file contains correct path Create a symlink points to a very long path, so that the path could not be hold in inode Check symlink contains the correct path 1023 chars are a bit long for golden image output, compute the md5 checksum success, all done. It is registered with `_begin_fstest auto quick metadata` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `360` plus `_begin_fstest auto quick metadata`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`, `_require_symlinks`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 18: `linkfile=$TEST_DIR/$seq.symlink`
- Line 21: `FNAME=$(perl -e 'print "a"x254')`
- Line 32: `status=0`

## Control Flow

The script runs linearly after the harness and requirement checks. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 15: `_require_test`
- Line 19: `rm -f $linkfile`
- Line 25: `ln -s $FNAME/$FNAME/$FNAME/$FNAME $linkfile`
- Line 29: `readlink $linkfile | md5sum`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `metadata`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`, `_require_symlinks`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Symlink persistence tests are metadata-focused and can fail through lost directory updates, wrong target payloads, or fast/slow symlink representation differences.

## Test Signals

The pass signal is filtered `md5sum` output, symlink target reads. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
