<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/321 -->
# sources/test-tools/xfstests/tests/btrfs/321

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/321_research.md`.

Source read: 85 lines, SHA256 prefix `bca0fdf15b2b6ff7`.

Purpose: FS QA Test 321 Make sure there are no use-after-free, crashes, deadlocks etc, when reading data which has its data checksums in a corrupted csum tree block..

Important APIs/types/functions: test tags `auto quick raid dangerous`; common harness imports `. ./common/preamble`; requirements/fixed gates `_require_scratch_nocheck`, `_require_scratch_dev_pool 2`, `_require_btrfs_raid_type raid0`, `_require_btrfs_support_sectorsize 4096`, `_require_btrfs_command inspect-internal dump-tree`, `_fixed_by_kernel_commit 10d9d8c3512f \`; key variables `iterations=32`, `physical=$(_btrfs_get_physical "$target_bytenr" 1)`, `dev=$(_btrfs_get_device_path "$target_bytenr" 1)`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L13: _require_scratch_nocheck; L14: _require_scratch_dev_pool 2; L18: _require_btrfs_raid_type raid0; L22: _require_btrfs_support_sectorsize 4096; L23: _require_btrfs_command inspect-internal dump-tree; L32: _scratch_pool_mkfs "-d raid0 -m single -n 4k -s 4k" >> $seqres.full 2>&1; L34: _scratch_mount -o datasum,datacow; L41: _scratch_unmount; L45: $BTRFS_UTIL_PROG inspect-internal dump-tree -t 7 $SCRATCH_DEV >> $seqres.full; L46: target_bytenr=$($BTRFS_UTIL_PROG inspect-internal dump-tree -t 7 $SCRATCH_DEV | grep "^leaf.*items" | sort | tail -n1 | cut -f2 -d\ ); L55: physical=$(_btrfs_get_physical "$target_bytenr" 1); L56: dev=$(_btrfs_get_device_path "$target_bytenr" 1); L65: _scratch_mount -o ro; L71: _scratch_unmount; L77: if _check_dmesg_for "BUG" ; then.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: bypasses normal scratch checking because corruption is intentional; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; absence or presence of expected dmesg warnings; btrfs on-disk tree inspection; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/321 -->
