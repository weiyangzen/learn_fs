<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/323 -->
# sources/test-tools/xfstests/tests/btrfs/323

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/323_research.md`.

Source read: 47 lines, SHA256 prefix `3d466767befaafa3`.

Purpose: FS QA Test 323 Test that remounted seed/sprout device FS is fully functional. For example, that it can purge stale subvolumes..

Important APIs/types/functions: test tags `auto quick seed remount volume`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_command "$BTRFS_TUNE_PROG" btrfstune`, `_require_scratch_dev_pool 2`, `_fixed_by_kernel_commit 70958a949d85 \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L13: _require_command "$BTRFS_TUNE_PROG" btrfstune; L14: _require_scratch_dev_pool 2; L19: _scratch_dev_pool_get 1; L23: _scratch_mkfs >>$seqres.full; L24: $BTRFS_TUNE_PROG -S 1 $SCRATCH_DEV; L25: _scratch_mount 2>&1 | _filter_scratch; L26: _btrfs device add -f $SPARE_DEV $SCRATCH_MNT >>$seqres.full; L30: _mount -o remount,rw $SCRATCH_MNT; L34: _btrfs subvolume create $SCRATCH_MNT/subv; L35: _btrfs subvolume delete $SCRATCH_MNT/subv; L38: _btrfs filesystem sync $SCRATCH_MNT; L41: $BTRFS_UTIL_PROG subvolume list -d $SCRATCH_MNT.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: mount/statfs option visibility.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/323 -->
