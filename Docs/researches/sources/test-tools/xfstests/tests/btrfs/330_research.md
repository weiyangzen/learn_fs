<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/330 -->
# sources/test-tools/xfstests/tests/btrfs/330

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/330_research.md`.

Source read: 54 lines, SHA256 prefix `b54447a997670636`.

Purpose: FS QA Test No. btrfs/330 Test mounting one subvolume as ro and another as rw.

Important APIs/types/functions: test tags `auto quick subvol`; common harness imports `. ./common/preamble`, `. ./common/filter.btrfs`; requirements/fixed gates `_fixed_by_kernel_commit cda7163d4e3d \`, `_require_scratch`; helper functions `_cleanup()`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`. Representative operation sequence: L28: _scratch_mkfs >> $seqres.full 2>&1 || _fail "mkfs failed"; L29: _scratch_mount; L32: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/foo | _filter_scratch; L33: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/bar | _filter_scratch; L35: _scratch_unmount; L40: _mount -t btrfs -o subvol=foo,ro $SCRATCH_DEV $TEST_DIR/$seq/foo; L41: _mount -t btrfs -o subvol=bar,rw $SCRATCH_DEV $TEST_DIR/$seq/bar.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: visible subtest labels include making sure foo is read only; making sure bar allows writes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/330 -->
