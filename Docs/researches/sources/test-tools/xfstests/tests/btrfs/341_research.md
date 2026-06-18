<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/341 -->
# sources/test-tools/xfstests/tests/btrfs/341

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/341_research.md`.

Source read: 73 lines, SHA256 prefix `e863503854b78d9d`.

Purpose: FS QA Test 341 Test renaming one directory over another one that has a subvolume inside it and fsync a file in the other directory that was previously renamed. We want to verify that after a power failure we are able to mount the filesystem and it has the correct content (all renames visible)..

Important APIs/types/functions: test tags `auto quick subvol rename log`; common harness imports `. ./common/preamble`, `. ./common/filter`, `. ./common/dmflakey`, `. ./common/renameat2`; requirements/fixed gates `_require_scratch`, `_require_dm_target flakey`, `_require_renameat2 exchange`, `_fixed_by_kernel_commit 7ba0b6461bc4 \`, `_require_metadata_journaling $SCRATCH_DEV`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L24: . ./common/renameat2; L28: _require_renameat2 exchange; L33: _scratch_mkfs >>$seqres.full 2>&1 || _fail "mkfs failed"; L36: _scratch_mount; L44: _btrfs subvolume create $SCRATCH_MNT/dir2/subvol; L47: _scratch_sync; L54: $here/src/renameat2 -x $SCRATCH_MNT/dir1 $SCRATCH_MNT/dir2; L63: $XFS_IO_PROG -c "fsync" $SCRATCH_MNT/dir2/bar.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; uses dm-flakey to simulate power loss.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates, xfs_io workload commands. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/341 -->
