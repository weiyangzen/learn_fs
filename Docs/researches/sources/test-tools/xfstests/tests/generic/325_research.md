# sources/test-tools/xfstests/tests/generic/325

## Purpose

Make some pages/extents of a file dirty, do a ranged fsync that covers only some of the dirty pages/extents, and then do a regular fsync (or another ranged fsync that covers the remaining dirty pages/extents) Verify after that all extents were persisted This test is motivated by a btrfs issue where the first ranged fsync would prevent the following fsync from persisting the remaining dirty pages/extents. This was fixed by the following btrfs kernel patch: Btrfs: fix fsync data loss after a ranged fsync. It is registered with `_begin_fstest auto quick data log mmap` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `325` plus `_begin_fstest auto quick data log mmap`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`. Capability gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. Local functions: `_cleanup`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 74: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 64 `echo "File content before crash/reboot:"`, line 69 `echo "File content after crash/reboot and fs mount:"`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 19: `_begin_fstest auto quick data log mmap`
- Line 31: `_require_scratch`
- Line 32: `_require_dm_target flakey`
- Line 34: `_scratch_mkfs >> $seqres.full 2>&1`
- Line 37: `_scratch_mount`
- Line 40: `$XFS_IO_PROG -f -c "pwrite -S 0xff 0 256K" $SCRATCH_MNT/foo | _filter_xfs_io`
- Line 45: `_scratch_sync`
- Line 55: `$XFS_IO_PROG \`
- Line 56: `-c "mmap -w 0 256K" \`
- Line 57: `-c "mwrite -S 0xaa 0 4K" \`
- Line 58: `-c "mwrite -S 0xbb 252K 4K" \`
- Line 59: `-c "msync -s 0K 64K" \`
- Line 60: `-c "msync -s 192K 64K" \`
- Line 72: `_scratch_unmount`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. dm-flakey is used to simulate a dropped write / power-fail boundary and then remount for recovery checks. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `auto`, `quick`, `data`, `log`, `mmap`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, and uses capability gates such as `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- mmap tests rely on page-cache writeback, timestamp granularity, and correct handling of dirty mappings across fsync, sync, or remount boundaries.
- Crash-recovery tests require dm-flakey behavior and metadata journaling; failures can appear as lost directory entries, stale content, or mount-time recovery errors.

## Test Signals

The pass signal is silence from the helper program and final `status=0`. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
