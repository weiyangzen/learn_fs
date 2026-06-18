<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/340 -->
# sources/test-tools/xfstests/tests/btrfs/340

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/340_research.md`.

Source read: 45 lines, SHA256 prefix `64efc1d6db416d08`.

Purpose: FS QA Test No. 340 Make sure when doing a quick inherit for snapshot, all parent qgroups including direct and indirect parents are properly updated..

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 68d4b3fa18d7 \`, `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_scratch_qgroup`; key variables `subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT subv1)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L18: _require_btrfs_qgroup_report; L21: _require_scratch_qgroup; L22: _scratch_mount; L26: _btrfs subvolume create $SCRATCH_MNT/subv1; L27: subvolid=$(_btrfs_get_subvolid $SCRATCH_MNT subv1); L28: _btrfs qgroup create 1/1 $SCRATCH_MNT; L29: _btrfs qgroup create 2/1 $SCRATCH_MNT; L30: _btrfs qgroup assign 1/1 2/1 $SCRATCH_MNT; L31: _btrfs qgroup assign 0/$subvolid 1/1 $SCRATCH_MNT; L35: _btrfs qgroup show -p --sync $SCRATCH_MNT >> $seqres.full; L40: _btrfs subv snap -i 1/1 $SCRATCH_MNT/subv1 $SCRATCH_MNT/snap1; L42: _btrfs qgroup show -p --sync $SCRATCH_MNT >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/340 -->
