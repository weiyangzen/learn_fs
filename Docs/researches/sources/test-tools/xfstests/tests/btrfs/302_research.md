<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/302 -->
# sources/test-tools/xfstests/tests/btrfs/302

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/302_research.md`.

Source read: 59 lines, SHA256 prefix `23a5bb5b911f2670`.

Purpose: FS QA Test 302 Test that snapshotting a new subvolume (created in the current transaction) that has a btree with a height > 1, works and does not result in a filesystem corruption. This exercises a regression introduced in kernel 6.5 by the kernel commit: 1b53e51a4a8f ("btrfs: don't commit transaction for every subvol create").

Important APIs/types/functions: test tags `auto quick snapshot subvol`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_require_scratch`, `_require_fssum`, `_fixed_by_kernel_commit eb96e221937a \`; key variables `fssum_file="$SCRATCH_MNT/checksum.fssum"`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L30: _scratch_mkfs -n 64K >> $seqres.full 2>&1 || _fail "mkfs failed"; L31: _scratch_mount; L33: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol | _filter_scratch; L43: $FSSUM_PROG -A -f -w $fssum_file $SCRATCH_MNT/subvol; L47: _btrfs subvolume snapshot -r $SCRATCH_MNT/subvol $SCRATCH_MNT/subvol/snap; L51: _scratch_cycle_mount; L55: $FSSUM_PROG -r $fssum_file $SCRATCH_MNT/subvol/snap.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/302 -->
