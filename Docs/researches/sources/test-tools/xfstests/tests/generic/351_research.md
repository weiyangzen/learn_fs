# sources/test-tools/xfstests/tests/generic/351

## Purpose

Test the unsupported fallocate flags on a block device. No collapse or insert range, no regular fallocate, no forgetting keep-space on zero range, no punching past EOD, no requests that aren't aligned with the logicalsector size, and make sure the fallbacks work for devices that don't support write_same or discard. It is registered with `_begin_fstest blockdev rw punch collapse insert zero prealloc` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `351` plus `_begin_fstest blockdev rw punch collapse insert zero prealloc`. Imported libraries: `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`. Capability gates: `_require_scsi_debug`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`, `_require_xfs_io_command "fpunch"`. Local functions: none. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 30: `dev=$(_get_scsi_debug_dev 4096 4096 0 4 "lbpws=1 lbpws10=1")`
- Line 51: `zod=$(_get_max_lfs_filesize)`
- Line 73: `dev=$(_get_scsi_debug_dev 512 512 0 4 "lbpws=0 lbpws10=0 lbpu=0 write_same_length=0 unmap_max_blocks=0")`
- Line 90: `status=0`

## Control Flow

The visible phases are driven by echo markers such as line 29 `echo "Create and format"`, line 34 `echo "Regular fallocate"`, line 37 `echo "Insert range"`, line 40 `echo "Collapse range"`. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `_require_xfs_io_command "falloc"`
- Line 26: `_require_xfs_io_command "fzero"`
- Line 27: `_require_xfs_io_command "fpunch"`
- Line 31: `_pwrite_byte 0x62 0 4m $dev >> $seqres.full`
- Line 32: `$XFS_IO_PROG -c "fsync" $dev`
- Line 34: `echo "Regular fallocate"`
- Line 35: `$XFS_IO_PROG -c "falloc 64k 64k" $dev`
- Line 38: `$XFS_IO_PROG -c "finsert 128k 64k" $dev`
- Line 41: `$XFS_IO_PROG -c "fcollapse 256k 64k" $dev`
- Line 44: `$XFS_IO_PROG -c "fzero -k 512 512" $dev`
- Line 47: `$XFS_IO_PROG -c "fpunch 512 512" $dev`
- Line 52: `$XFS_IO_PROG -c "fzero -k 512k $zod" $dev`
- Line 55: `$XFS_IO_PROG -c "fzero 512k $zod" $dev`
- Line 84: `md5sum $dev | sed -e "s|$dev|SCSI_DEBUG_DEV|g"`

## State and Persistence Behavior

The script has little persistent state beyond the files it creates and the xfstests result logs. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `blockdev`, `rw`, `punch`, `collapse`, `insert`, `zero`, `prealloc`, imports `. ./common/preamble`, `. ./common/filter`, `. ./common/scsi_debug`, and uses capability gates such as `_require_scsi_debug`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "finsert"`, `_require_xfs_io_command "fcollapse"`, `_require_xfs_io_command "fzero"`, `_require_xfs_io_command "fpunch"`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Block-device fallocate tests rely on scsi_debug discard/write-same emulation and logical-sector alignment, not normal mounted filesystem behavior.

## Test Signals

The pass signal is filtered `md5sum` output. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
