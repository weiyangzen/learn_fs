<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/331 -->
# sources/test-tools/xfstests/tests/btrfs/331

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/331_research.md`.

Source read: 43 lines, SHA256 prefix `22a0a1276f6e1f6a`.

Purpose: FS QA Test 331 Test that btrfs does not recycle subvolume ids across remounts in a way that breaks squotas..

Important APIs/types/functions: test tags `auto quick qgroup snapshot`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 2b8aa78cf127 \`, `_require_scratch_enable_simple_quota`; key variables `sv=$SCRATCH_MNT/sv`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L16: _require_scratch_enable_simple_quota; L18: _scratch_mkfs >> $seqres.full; L19: _scratch_mount; L20: $BTRFS_UTIL_PROG quota enable --simple $SCRATCH_MNT; L25: $BTRFS_UTIL_PROG subvolume create $sv.$i >> $seqres.full; L28: $BTRFS_UTIL_PROG subvolume delete $sv.$i >> $seqres.full; L32: _scratch_cycle_mount; L35: $BTRFS_UTIL_PROG subvolume create $sv.BOOM >> $seqres.full; L37: $BTRFS_UTIL_PROG subvolume snapshot $sv.BOOM $sv.BOOM.$i >> $seqres.full.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes; persists snapshot roots and verifies their contents; changes quota/qgroup accounting state.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: quota accounting regressions can be silent until unmount or rescan; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/331 -->
