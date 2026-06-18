# sources/test-tools/xfstests/tests/generic/310

## Purpose

Check if there are two threads,one keeps calling read() or lseek(), and the other calling readdir(), both on the same directory fd Testing on ext3: with dir_index disabled results in the following dmesg output: (also occurs when testing ext2 and ext4) EXT3-fs error (device sdb): ext3_readdir: bad entry in directory #1134241: rec_len % 4 != 0 - offset=2704, inode=16973836, rec_len=12850, name_len=52 EXT3-fs error (device sdb): ext3_readdir: bad entry in directory #1134241: directory entry across blocks - offset=1672, inode=16973836, rec_len=14132, name_len=57 The filesystem mount option 'errors=' will define the behavior when an error is encountered. (see mount manpage) The test is based on a testcase from Li Zefan <lizefan@huawei.com> http://marc.info/?l=linux-kernel&m=136123703211869&w=2. It is registered with `_begin_fstest auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `310` plus `_begin_fstest auto`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_test`. Local functions: `_cleanup`, `check_kernel_bug`, `_test_read`, `_test_lseek`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 45: `nr_bug=`dmesg | grep -c "kernel BUG"``
- Line 46: `nr_null=`dmesg | grep -c "kernel NULL pointer dereference"``
- Line 47: `nr_warning=`dmesg | grep -c "^WARNING"``
- Line 48: `nr_lockdep=`dmesg | grep -c "possible recursive locking detected"``
- Line 53: `new_bug=`dmesg | grep -c "kernel BUG"``
- Line 54: `new_null=`dmesg | grep -c "kernel NULL pointer dereference"``
- Line 55: `new_warning=`dmesg | grep -c "^WARNING"``
- Line 56: `new_lockdep=`dmesg | grep -c "possible recursive locking detected"``

## Control Flow

The visible phases are driven by echo markers such as line 113 `echo "*** done"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 32: `_pkill -9 $seq.t_readdir > /dev/null 2>&1`
- Line 34: `rm -rf $TEST_DIR/tmp`
- Line 35: `rm -f $tmp.*`
- Line 41: `_require_test`
- Line 77: `mkdir -p $SEQ_DIR`
- Line 79: `touch $SEQ_DIR/$n`
- Line 82: `_test_read()`
- Line 86: `_pkill -PIPE $seq.t_readdir_1`
- Line 95: `_test_lseek()`
- Line 100: `_pkill -PIPE $seq.t_readdir_2`
- Line 109: `_test_read`
- Line 110: `_test_lseek`

## State and Persistence Behavior

Primary state lives under `$TEST_DIR`, making this a test-device workload rather than a scratch-device destructive test. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_test`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
