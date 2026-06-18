# sources/test-tools/xfstests/tests/generic/219

## Purpose

Simple quota accounting test for direct/buffered/mmap IO. It is registered with `_begin_fstest auto quota quick mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `219` plus `_begin_fstest auto quota quick mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`. Capability gates: `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_odirect`. Local functions: `test_files`, `check_usage`, `_round_up_to_fs_blksz`, `test_accounting`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 37: `wroteblocks=$1`
- Line 38: `wrotefiles=$2`
- Line 65: `io_sz=$(_round_up_to_fs_blksz 48)`
- Line 66: `sz=$(( io_sz * 3 ))`
- Line 84: `id=$qa_user`
- Line 86: `id=$qa_group`
- Line 104: `type=u`
- Line 113: `type=g`

## Control Flow

The visible phases are driven by echo markers such as line 25 `echo; echo "### create files, setting up ownership (type=$type)"`, line 41 `echo "Too few blocks used (type=$type)"`, line 44 `echo "Too many blocks used (type=$type)"`, line 46 `echo "Bad number of inodes used (type=$type)"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 11: `_begin_fstest auto quota quick mmap`
- Line 17: `_require_scratch`
- Line 26: `rm -f $SCRATCH_MNT/{buffer,direct,mmap}`
- Line 28: `chown $qa_user $SCRATCH_MNT/{buffer,direct,mmap}`
- Line 30: `for file in $SCRATCH_MNT/{buffer,direct,mmap}; do`
- Line 68: `echo "### some controlled buffered, direct and mmapd IO (type=$type)"`
- Line 72: `$XFS_IO_PROG -c 'pwrite 0 48k' -d \`
- Line 75: `$SCRATCH_MNT/mmap >>$seqres.full 2>&1 &`
- Line 80: `$here/src/lstat64 $file | head -2 | _filter_scratch`
- Line 92: `_scratch_unmount 2>/dev/null`
- Line 94: `_scratch_mount "-o usrquota,grpquota"`
- Line 96: `quotacheck -u -g $SCRATCH_MNT 2>/dev/null`
- Line 98: `_scratch_unmount`
- Line 116: `_scratch_unmount 2>/dev/null`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Quota state is persistent filesystem metadata manipulated through `quotacheck`, `quotaon`, `setquota`, and `repquota` across user and group modes. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quota`, `quick`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/quota`, and uses capability gates such as `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_odirect`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Quota tests depend on kernel quota mode, grace-period timing, and the qa user/group setup; stale quota files or unsupported VFS quota behavior can turn a real failure into a notrun or noisy output mismatch.
- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.

## Test Signals

The pass signal is quota usage/enforcement reports, stat/lstat metadata output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
