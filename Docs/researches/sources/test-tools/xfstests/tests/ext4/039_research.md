<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/039 -->
# sources/test-tools/xfstests/tests/ext4/039

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/039_research.md`.

Source read: 81 lines, SHA256 prefix `8673ecea49839ecc`.

Purpose: FSQA Test No. ext4/039 Test data journaling flag switch for a single file ext3 and ext4 don't support direct IO in journalling mode.

Important APIs/types/functions: test tags `auto enospc rw`; common harness imports `. ./common/preamble`, `. ./common/filter`; requirements/fixed gates `_exclude_fs ext2`, `_require_scratch`, `_exclude_scratch_mount_option dax`; helper functions `_workout()`; key variables `write_opt_list="iflag=noatime conv=notrunc conv=fsync"`, `chattr_opt_list="+j -j +jS -j"`, `idx=0`, `idx=$((idx + 1))`, `bs=1M count=4 $write_opt \`, `idx=$((idx + 1))`, `bs=1M $write_opt >> $seqres.full 2>&1`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_workout()`. Representative operation sequence: L62: _exclude_scratch_mount_option dax; L64: _scratch_mkfs_sized $((64 * 1024 * 1024)) >> $seqres.full 2>&1; L65: _scratch_mount; L69: _scratch_unmount; L74: if ! _scratch_unmount; then.

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems.

Dependencies and integration points: Depends on xfstests common libraries. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: depends on xfstests harness requirements and exact golden-output filtering.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Switch data journalling mode. Silence is golden.; workout failed; failed to umount; Check filesystem.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/039 -->
