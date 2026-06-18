<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/317 -->
# sources/test-tools/xfstests/tests/btrfs/317

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/317_research.md`.

Source read: 66 lines, SHA256 prefix `9a025ce7549594ef`.

Purpose: FS QA Test 317 Test that btrfs convert can ony be run to convert to supported profiles on a zoned filesystem.

Important APIs/types/functions: test tags `auto volume raid convert`; common harness imports `. ./common/preamble`, `. common/filter.btrfs`; requirements/fixed gates `_fixed_by_kernel_commit 5906333cc4af \`, `_require_scratch_dev_pool 4`, `_require_zoned_device "$SCRATCH_DEV"`; key variables `devs=( $SCRATCH_DEV_POOL )`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L18: _require_scratch_dev_pool 4; L24: _scratch_mkfs -msingle -dsingle 2>&1 >> $seqres.full || _fail "mkfs failed"; L25: _scratch_mount; L28: _run_btrfs_balance_start -f -mconvert=dup -sconvert=dup $SCRATCH_MNT 2>&1 |\; L32: _run_btrfs_balance_start -dconvert=dup $SCRATCH_MNT 2>&1 |\; L36: $BTRFS_UTIL_PROG device add ${devs[1]} $SCRATCH_MNT | _filter_device_add; L39: _run_btrfs_balance_start -dconvert=raid1 $SCRATCH_MNT 2>&1 |\; L43: _run_btrfs_balance_start -dconvert=raid0 $SCRATCH_MNT 2>&1 |\; L47: $BTRFS_UTIL_PROG device add ${devs[2]} $SCRATCH_MNT | _filter_device_add; L50: _run_btrfs_balance_start -f -dconvert=raid5 $SCRATCH_MNT 2>&1 |\; L54: $BTRFS_UTIL_PROG device add ${devs[3]} $SCRATCH_MNT | _filter_device_add; L57: _run_btrfs_balance_start -dconvert=raid10 $SCRATCH_MNT 2>&1 |\; L61: _run_btrfs_balance_start -f -dconvert=raid6 $SCRATCH_MNT 2>&1 |\.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: successful script exit with xfstests filtered output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/317 -->
