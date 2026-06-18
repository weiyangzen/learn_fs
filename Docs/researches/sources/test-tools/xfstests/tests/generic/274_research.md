# sources/test-tools/xfstests/tests/generic/274

## Purpose

preallocation test: Preallocate space to a file, and fill the rest of the fs to 100% Then test a write into that preallocated space, which should succeed creator Compression can exhaust metadata space here for btrfs and cause spurious failurs because we hit a metadata ENOSPC, skip if we have compression enabled. It is registered with `_begin_fstest auto rw prealloc enospc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `274` plus `_begin_fstest auto rw prealloc enospc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_no_compress`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 16: `status=0 # success is the default!`

## Control Flow

The visible phases are driven by echo markers such as line 35 `echo "------------------------------"`, line 36 `echo "preallocation test"`, line 37 `echo "------------------------------"`, line 49 `echo "Fill fs with 1M IOs; ENOSPC expected" >> $seqres.full`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 22: `rm -f $tmp.*`
- Line 23: `_scratch_unmount`
- Line 28: `_require_scratch`
- Line 29: `_require_xfs_io_command "falloc" "-k"`
- Line 39: `_scratch_unmount 2>/dev/null`
- Line 40: `_scratch_mkfs_sized $((2 * 1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- Line 41: `_scratch_mount`
- Line 44: `$XFS_IO_PROG -f -c "pwrite 0 64k" -c "falloc -k 64k 64m" $SCRATCH_MNT/test \`
- Line 50: `dd if=/dev/zero of=$SCRATCH_MNT/tmp1 bs=1M >>$seqres.full 2>&1`
- Line 52: `dd if=/dev/zero of=$SCRATCH_MNT/tmp2 bs=4K >>$seqres.full 2>&1`
- Line 53: `_scratch_sync`
- Line 56: `dd if=/dev/zero of=$SCRATCH_MNT/tmp3 bs=4K oflag=sync >>$seqres.full 2>&1`
- Line 59: `df $SCRATCH_MNT >>$seqres.full 2>&1`
- Line 77: `_scratch_sync`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `rw`, `prealloc`, `enospc`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`, `_require_no_compress`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- ENOSPC cases are deliberately capacity-sensitive and can expose allocator, reservation, or delayed-allocation leaks only when scratch sizing and reserved blocks match the scenario.

## Test Signals

The pass signal is explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
