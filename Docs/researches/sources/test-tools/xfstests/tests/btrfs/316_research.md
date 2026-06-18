<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/316 -->
# sources/test-tools/xfstests/tests/btrfs/316

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/316_research.md`.

Source read: 59 lines, SHA256 prefix `194649daaae65538`.

Purpose: FS QA Test 316 Make sure btrfs qgroup won't leak its reserved data space if qgroup is marked inconsistent. This exercises a regression introduced in v6.1 kernel by the following commit: e15e9f43c7ca ("btrfs: introduce BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING to skip qgroup accounting").

Important APIs/types/functions: test tags `auto quick qgroup`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch`, `_require_qgroup_rescan`, `_fixed_by_kernel_commit d139ded8b9cd \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L23: _scratch_mkfs >> $seqres.full; L24: _scratch_mount; L26: $BTRFS_UTIL_PROG quota enable $SCRATCH_MNT; L29: $BTRFS_UTIL_PROG qgroup create 1/0 $SCRATCH_MNT >> $seqres.full; L30: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subv1 >> $seqres.full; L36: $BTRFS_UTIL_PROG subvolume snapshot -i 1/0 $SCRATCH_MNT/subv1 $SCRATCH_MNT/snap1 >> $seqres.full; L44: _scratch_unmount.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; absence or presence of expected dmesg warnings; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/316 -->
