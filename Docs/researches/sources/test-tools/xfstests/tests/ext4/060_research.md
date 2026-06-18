<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/060 -->
# sources/test-tools/xfstests/tests/ext4/060

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/ext4/060_research.md`.

Source read: 51 lines, SHA256 prefix `0a8ce18c4c8ca457`.

Purpose: FS QA Test 060 This test ensures that kernel avoids FS corruption while online resizing an ext4 filesystem with disabled resize_inode feature. The commit a6b3bfe176e8 ("ext4: fix corruption during on-line resize") stops the corruption..

Important APIs/types/functions: test tags `auto resize quick`; common harness imports `. ./common/preamble`; requirements/fixed gates `_exclude_fs ext2`, `_exclude_fs ext3`, `_fixed_by_kernel_commit a6b3bfe176e8 \`, `_require_command "$RESIZE2FS_PROG" resize2fs`, `_require_command "$E2FSCK_PROG" e2fsck`, `_require_scratch_size_nocheck $((9* 1024 * 1024))`; key variables `dev_size=$((8* 1024 * 1024 * 1024 - 128 * 1024 * 1024))`, `MKFS_OPTIONS="-O ^resize_inode" _scratch_mkfs_sized $dev_size \`.

Control flow: The script is mostly straight-line after harness setup. Representative operation sequence: L20: if __scratch_uses_fsdax && [[ $(_get_page_size) -ne 4096 ]]; then; L27: _require_command "$RESIZE2FS_PROG" resize2fs; L28: _require_command "$E2FSCK_PROG" e2fsck; L29: _require_scratch_size_nocheck $((9* 1024 * 1024)); L36: MKFS_OPTIONS="-O ^resize_inode" _scratch_mkfs_sized $dev_size \; L39: _scratch_mount; L42: $RESIZE2FS_PROG $SCRATCH_DEV 9G >> $seqres.full 2>&1; L44: _scratch_unmount; L46: $E2FSCK_PROG -fn $SCRATCH_DEV >> $seqres.full 2>&1 || _fail "Filesystem corrupted".

State and persistence behavior: formats scratch or loop-backed filesystems; mounts and unmounts test filesystems; uses fsck as the final persistence/integrity oracle; resizes filesystem images or online filesystems.

Dependencies and integration points: Depends on xfstests common libraries, e2fsprogs debug/fsck utilities. The file is integrated by the xfstests group list/build system and uses `$SCRATCH_DEV`, `$SCRATCH_MNT`, `$TEST_DIR`, `$seqres.full`, and filtered stdout as its contract with the harness.

Risks: is tied to specific kernel-regression behavior noted by fixed-by annotations.

Test signals: no unexpected stdout beyond the golden quiet marker; clean e2fsck verification; visible subtest labels include Silence is golden.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/ext4/060 -->
