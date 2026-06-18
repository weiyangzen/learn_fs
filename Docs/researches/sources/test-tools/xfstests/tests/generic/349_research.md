# sources/test-tools/xfstests/tests/generic/349

## Purpose

Test fallocate(ZERO_RANGE) on a block device, which should be able to WRITE SAME (or equivalent) the range. It is registered with `_begin_fstest blockdev rw zero` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `349` plus `_begin_fstest blockdev rw zero`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`. Capability gates: `_require_scsi_debug`, `_require_xfs_io_command "fzero"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 23: `dev=$(_get_scsi_debug_dev 512 512 0 4 "lbpws=1 lbpws10=1")`
- Line 40: `zod=$(_get_max_lfs_filesize)`
- Line 50: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 22 `echo "Create and format"`, line 26 `echo "Zero range"`, line 29 `echo "Zero range without keep_size"`, line 32 `echo "Zero range past EOD"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 20: `_require_xfs_io_command "fzero"`
- Line 24: `_pwrite_byte 0x62 0 4m $dev >> $seqres.full`
- Line 27: `$XFS_IO_PROG -c "fzero -k 512k 1m" $dev`
- Line 30: `$XFS_IO_PROG -c "fzero 384k 64k" $dev`
- Line 33: `$XFS_IO_PROG -c "fzero -k 3m 4m" $dev`
- Line 36: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`
- Line 41: `$XFS_IO_PROG -c "fzero -k 0 $zod" $dev`
- Line 44: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`

## State and Persistence Behavior

The script has little persistent state beyond the files it creates and the xfstests result logs. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `blockdev`, `rw`, `zero`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`, and uses capability gates such as `_require_scsi_debug`, `_require_xfs_io_command "fzero"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
