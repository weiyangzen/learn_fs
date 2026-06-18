<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/326 -->
# sources/test-tools/xfstests/tests/btrfs/326

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/326_research.md`.

Source read: 112 lines, SHA256 prefix `606edf534c02efa5`.

Purpose: FS QA Test No. 326 Test that mounting a subvolume read-write will success, with another subvolume being remounted RO/RW at background.

Important APIs/types/functions: test tags `auto quick mount remount`; common harness imports `. ./common/preamble`; requirements/fixed gates `_fixed_by_kernel_commit 951a3f59d268 \`, `_fixed_by_kernel_commit 344bac8f0d73 \`, `_require_test`, `_require_scratch`; helper functions `_cleanup()`, `remount_workload()`, `mount_workload()`; key variables `subv1_mount="$TEST_DIR/subvol1_mount"`, `subv2_mount="$TEST_DIR/subvol2_mount"`, `remount_pid=$!`, `mount_pid=$!`.

Control flow: The script defines reusable helpers first, then executes them from the bottom of the file. Defined helpers are `_cleanup()`, `remount_workload()`, `mount_workload()`. Representative operation sequence: L28: $UMOUNT_PROG "$subv1_mount" &> /dev/null; L29: $UMOUNT_PROG "$subv2_mount" &> /dev/null; L30: rm -rf -- "$subv1_mount" "$subv2_mount"; L37: _scratch_mkfs >> $seqres.full 2>&1; L38: _scratch_mount; L39: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol1 >> $seqres.full; L40: $BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/subvol2 >> $seqres.full; L41: _scratch_unmount; L43: subv1_mount="$TEST_DIR/subvol1_mount"; L44: subv2_mount="$TEST_DIR/subvol2_mount"; L45: rm -rf "$subv1_mount" "$subv2_mount"; L46: mkdir -p "$subv1_mount"; L47: mkdir -p "$subv2_mount"; L48: _mount "$SCRATCH_DEV" "$subv1_mount" -o subvol=subvol1; L56: _mount -o remount,ro "$subv1_mount"; L57: _mount -o remount,rw "$subv1_mount"; L82: _mount "$SCRATCH_DEV" "$subv2_mount"; L83: $UMOUNT_PROG "$subv2_mount".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; creates or manipulates btrfs subvolumes.

Dependencies and integration points: Depends on xfstests common libraries, btrfs-progs and btrfs kernel feature gates. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: contains timing-sensitive waits; is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/326 -->
