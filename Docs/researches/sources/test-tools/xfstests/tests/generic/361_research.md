# sources/test-tools/xfstests/tests/generic/361

## Purpose

Test remount on I/O errors XFS had a bug to hang on remount in this case, this kernel commit fix the issue 5cb13dc cancel the setfilesize transation when io error happen create a small filesystem to hold another filesystem image. It is registered with `_begin_fstest auto quick` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `361` plus `_begin_fstest auto quick`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_block_device $SCRATCH_DEV`, `_require_loop`, `_require_sparse_files`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 38: `fs_img=$SCRATCH_MNT/fs.img`
- Line 39: `fs_mnt=$SCRATCH_MNT/mnt`
- Line 44: `loop_dev=$(_create_loop_device $fs_img)`
- Line 49: `dname=$(_short_dev $loop_dev)`
- Line 63: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo 0 | tee /sys/fs/xfs/$dname/error/*/*/* > /dev/null`, line 62 `echo "Silence is golden"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_unmount $fs_mnt &>> /dev/null`
- Line 22: `rm -f $tmp.*`
- Line 28: `_require_scratch`
- Line 34: `_scratch_mkfs_sized $((512 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 35: `_scratch_mount`
- Line 40: `$XFS_IO_PROG -fc "truncate 1g" $fs_img >>$seqres.full 2>&1`
- Line 41: `mkdir -p $fs_mnt`
- Line 46: `_mount -t $FSTYP $loop_dev $fs_mnt`
- Line 52: `$XFS_IO_PROG -fc "pwrite 0 520m" $fs_mnt/testfile >>$seqres.full 2>&1`
- Line 55: `$MOUNT_PROG -o remount,ro $fs_mnt >>$seqres.full 2>&1`
- Line 57: `_unmount $fs_mnt &>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_block_device $SCRATCH_DEV`, `_require_loop`, `_require_sparse_files`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- The main risk is environment drift: missing helper binaries, unsupported filesystem operations, or output formatting changes can make the test skip or fail without indicating a filesystem regression.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
