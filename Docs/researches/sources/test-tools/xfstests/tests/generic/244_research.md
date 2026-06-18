# sources/test-tools/xfstests/tests/generic/244

## Purpose

test out "sparse" quota ids retrieved by Q_GETNEXTQUOTA Designed to use the new Q_GETNEXTQUOTA quotactl. It is registered with `_begin_fstest auto quick quota` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `244` plus `_begin_fstest auto quick quota`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_quota`, `_require_scratch`, `_require_getnextquota`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 32: `TYPES="u g"`
- Line 33: `MOUNT_OPTIONS="-o usrquota,grpquota"`
- Line 45: `ITERATIONS=100`
- Line 49: `ID=`od -N 4 -t uI -An /dev/urandom | tr -d " "``
- Line 77: `NEXT=1`
- Line 80: `Q=`$here/src/test-nextquota -i $NEXT -${TYPE} -d $SCRATCH_DEV` \`
- Line 86: `NEXT=`echo "$Q" | grep ^id | awk '{print $NF}' | head -n 1``
- Line 93: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 37 `echo "Launch all quotas"`, line 50 `echo $ID >> $tmp.1`, line 79 `echo "Trying ID $NEXT expecting $ID" >> $seqres.full`, line 82 `echo $Q >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 12: `_begin_fstest auto quick quota`
- Line 19: `rm -f $tmp.*`
- Line 24: `. ./common/quota`
- Line 27: `_require_quota`
- Line 28: `_require_scratch`
- Line 30: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 33: `MOUNT_OPTIONS="-o usrquota,grpquota"`
- Line 34: `_qmount`
- Line 35: `_require_getnextquota`
- Line 37: `echo "Launch all quotas"`
- Line 60: `setquota -${TYPE} $ID $ID $ID $ID $ID $SCRATCH_MNT`
- Line 61: `touch ${SCRATCH_MNT}/${ID}`
- Line 62: `chown ${ID} ${SCRATCH_MNT}/${ID}`
- Line 81: `|| _fail "test-nextquota failed: $Q"`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `quota`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_quota`, `_require_scratch`, `_require_getnextquota`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
