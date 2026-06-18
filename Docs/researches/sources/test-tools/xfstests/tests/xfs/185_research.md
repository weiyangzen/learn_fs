<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/185 -->
# sources/test-tools/xfstests/tests/xfs/185

## Purpose
`sources/test-tools/xfstests/tests/xfs/185` is a preallocation/unwritten extent regression. Regression test for commits: c02f6529864a ("xfs: make xfs_rtalloc_query_range input parameters const") 9ab72f222774 ("xfs: fix off-by-one error when the last rt extent is in use") 7e1826e05ba6 ("xfs: make fsmap backend function key parameters const") These commits fix a bug in fsmap where the data device fsmap function would corrupt the high key passed to the rt fsmap function if the data device number is smaller than the rt device number and the data device itself is smaller than the rt device. The `_begin_fstest` declaration is `auto fsmap prealloc punch`, which places the case in the corresponding fstests groups.

## Important APIs, Types, And Functions
The script is a bash fstests case built on `./common/preamble` and imports `./common/preamble`. Local helper surface: `_cleanup`, `rtfile_exts`, `fsmap`. Requirement gates: `_require_test`, `_require_loop`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "fsmap"`. Important external or harness commands observed in the full source include `chattr`, `mount`, `umount`, `xfs_rtalloc_query_range`. Notable scenario variables include state is mostly implicit in harness variables.

## Control Flow
After declaring the fstest, the script performs requirement checks, prepares scratch/test state, and then executes the scenario-specific filesystem operations. The concrete flow mounts, remounts, or deliberately rejects mounts through fstests helpers; drives file layout with xfs_io operations such as fallocate, punch, zero, bmap, fiemap, fsync, direct I/O, or mmap. Output is either matched directly against the companion `.out` file or normalized through imported filter helpers.

## State And Persistence Behavior
Persistent effects are intentionally scoped to scratch/test filesystem contents, temporary `$tmp.*` files, diagnostic `$seqres.full` logs, loop devices and loop-mounted images. Cleanup is handled by the local `_cleanup` function when present and otherwise by the fstests harness.

## Dependencies And Integration Points
Integration is through the fstests XFS harness variables such as `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres`, `$seqres.full`, and tool variables including `$XFS_IO_PROG`, `$XFS_DB_PROG`, `$XFS_REPAIR_PROG`, `$MKFS_XFS_PROG`, or quota/dump-specific programs when used. The requirement gates are the compatibility contract that skip unsupported kernels, xfsprogs versions, filesystems, devices, or userland tools before assertions run.

## Risks
intentional metadata corruption can leave the scratch device unmountable until repair or cleanup completes; loop-device setup and teardown must be exact to avoid leaked mounts or stale devices; all cases rely on correct fstests environment variables and scratch/test device hygiene.

## Test Signals
companion golden output `sources/test-tools/xfstests/tests/xfs/185.out`; stable progress labels including `echo "data device ($ddbytes) has more bytes than rt ($rtbytes)"`, `echo "rtbytes $rtbytes rtfreebytes $rtfreebytes rtextsize $rtextsize" >> $seqres.full`, `echo "allocrtx $alloc_rtx falloc $((alloc_rtx * rtextsize))" >> $seqres.full`, `echo "$foff $fend $physoff $physend"`; diagnostic detail captured in `$seqres.full`; harness failures through command exit status, `_fail`, `_notrun`, and post-test filesystem checks; the source has 211 lines and was read completely for this report.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/185 -->
